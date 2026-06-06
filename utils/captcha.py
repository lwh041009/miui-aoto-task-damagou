"""人机验证处理（可插拔）"""

import json
import time
from traceback import print_exc

from jsonpath_ng import parse
from jsonpath_ng.exceptions import JsonPathParserError

from .captcha_solver import CaptchaTask
from .config import ConfigManager
from .data_model import GeetestResult
from .logger import log
from .request import request

_conf = ConfigManager.data_obj


def find_key(data: dict, key: str):
    """递归查找字典中的key"""
    for dkey, dvalue in data.items():
        if dkey == key:
            return dvalue
        if isinstance(dvalue, dict):
            find_key(dvalue, key)
    return None


SOLVERS = []


def register_solver(solver):
    if solver and solver not in SOLVERS:
        SOLVERS.append(solver)


try:
    from damagou_adapter import DamagouSolver

    register_solver(DamagouSolver())
except Exception:  # pylint: disable=broad-exception-caught
    log.warning("打码狗验证码解算器注册失败，将尝试其他方案")


def get_validate_other(gt: str, challenge: str, result: str) -> GeetestResult:
    """获取人机验证结果"""
    try:
        validate = ""
        if _conf.preference.get_geetest_url:
            params = _conf.preference.get_geetest_params.copy()
            params = json.loads(
                json.dumps(params)
                .replace("{gt}", gt)
                .replace("{challenge}", challenge)
                .replace("{result}", str(result))
            )
            data = _conf.preference.get_geetest_data.copy()
            data = json.loads(
                json.dumps(data)
                .replace("{gt}", gt)
                .replace("{challenge}", challenge)
                .replace("{result}", str(result))
            )
            for i in range(_conf.preference.get_geetest_try_count):
                log.info(f"第{i}次获取结果")
                response = request(
                    _conf.preference.get_geetest_method,
                    _conf.preference.get_geetest_url,
                    params=params,
                    json=data,
                )
                log.debug(response.text)
                result = response.json()
                geetest_validate_expr = parse(_conf.preference.get_geetest_validate_path)
                geetest_validate_match = geetest_validate_expr.find(result)
                if len(geetest_validate_match) > 0:
                    validate = geetest_validate_match[0].value
                geetest_challenge_expr = parse(_conf.preference.get_geetest_challenge_path)
                geetest_challenge_match = geetest_challenge_expr.find(result)
                if len(geetest_challenge_match) > 0:
                    challenge = geetest_challenge_match[0].value
                if validate and challenge:
                    return GeetestResult(challenge=challenge, validate=validate)
                time.sleep(1)
            return GeetestResult(challenge="", validate="")
        return GeetestResult(challenge="", validate="")
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception("获取人机验证结果异常")
        return GeetestResult(challenge="", validate="")


def _solve_with_registered_solvers(task: CaptchaTask) -> GeetestResult:
    for solver in SOLVERS:
        try:
            log.info(f"尝试验证码解算器: {getattr(solver, 'name', solver.__class__.__name__)}")
            result = solver.solve(task)
            # 极验3代：validate 字段有值；极验4代：lot_number/pass_token 有值
            if result and (result.validate or result.lot_number):
                return result
        except Exception:
            log.exception("验证码解算器执行异常")
    return GeetestResult(challenge="", validate="")


def get_validate(gt: str, challenge: str) -> GeetestResult:
    """创建人机验证并结果"""
    try:
        result = ""
        # 先尝试注册的解算器（打码狗等），无论是否配置geetest_url
        task = CaptchaTask(gt=gt, challenge=challenge)
        solved = _solve_with_registered_solvers(task)
        if solved and (solved.validate or solved.lot_number):
            return solved

        if _conf.preference.geetest_url:
            params = _conf.preference.get_geetest_params.copy()
            params = json.loads(
                json.dumps(params).replace("{gt}", gt).replace("{challenge}", challenge)
            )
            data = _conf.preference.get_geetest_data.copy()
            data = json.loads(
                json.dumps(data).replace("{gt}", gt).replace("{challenge}", challenge)
            )
            response = request(
                _conf.preference.get_geetest_method,
                _conf.preference.get_geetest_url,
                params=params,
                json=data,
            )
            log.debug(response.text)
            result = response.json()
            try:
                geetest_validate_expr = parse(_conf.preference.get_geetest_validate_path)
                geetest_validate_match = geetest_validate_expr.find(result)
                validate = geetest_validate_match[0].value if geetest_validate_match else ""
                geetest_challenge_expr = parse(_conf.preference.get_geetest_challenge_path)
                geetest_challenge_match = geetest_challenge_expr.find(result)
                challenge = geetest_challenge_match[0].value if geetest_challenge_match else ""
                geetest_result_expr = parse(_conf.preference.get_geetest_result_path)
                geetest_result_match = geetest_result_expr.find(result)
                result = geetest_result_match[0].value if geetest_result_match else result
            except JsonPathParserError:
                print_exc()
            if validate and challenge:
                return GeetestResult(challenge=challenge, validate=validate)
            return get_validate_other(gt=gt, challenge=challenge, result=result)
        return GeetestResult(challenge="", validate="")
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception("获取人机验证结果异常")
        return GeetestResult(challenge="", validate="")
