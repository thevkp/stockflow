# in a new file: utils/decorators.py
from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Union, Tuple, Literal, Any, Dict, cast
from flask import jsonify
from flask.wrappers import Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt # type: ignore

P = ParamSpec("P")
R = TypeVar("R")

def role_required(required_role: str) -> Callable[[Callable[P, R]], Callable[P, Union[R, Tuple[Response, Literal[403]]]]]:
    def decorator(fn: Callable[P, R]) -> Callable[P, Union[R, Tuple[Response, Literal[403]]]]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Union[R, Tuple[Response, Literal[403]]]:
            verify_jwt_in_request()
            # get_jwt() has a loosely-typed return; cast to a more specific type
            claims: Dict[str, Any] = cast(Dict[str, Any], get_jwt())
            if claims.get("role") != required_role:
                return jsonify({"error": "insufficient permissions"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator