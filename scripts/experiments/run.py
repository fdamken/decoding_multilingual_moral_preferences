import traceback
from logging import Logger
from typing import Any, Optional

from tqdm import tqdm

import model
import moral_machine
from agent import Agent
from api_usage import APIUsage
from experiment import ex


def _run_session(agent: Agent, session: moral_machine.Session) -> tuple[list[int], APIUsage]:
    try:
        result = agent.play(session)
    except Exception:
        result = traceback.format_exc()
    return result, agent.report_api_usage()


@ex.automain
def main(model_name: str, language: str, session_indices: Optional[int | list[int]], _log: Logger) -> Any:
    assert model_name in model.get_available_models(), f"model '{model_name}' not available"
    assert language in moral_machine.get_available_languages(), f"language '{language}' not available"

    if session_indices is not None:
        if type(session_indices) is int:
            session_indices = [session_indices]
        _log.info(f"playing only sessions {session_indices}")

    answers: list[list[int]] = []
    api_usage: list[APIUsage] = []
    sessions = moral_machine.load_sessions(language)
    agent = Agent(model_name)
    total = len(session_indices) if session_indices is not None else len(sessions)
    with tqdm(total=total) as pbar:
        for session_idx, session in enumerate(sessions):
            if session_indices is None or session_idx in session_indices:
                session_answers, session_api_usage = _run_session(agent, session)
                pbar.update()
            else:
                session_answers, session_api_usage = f"skipped; only playing sessions {session_indices}", APIUsage(model_name, 0, 0, 0)
            answers.append(session_answers)
            api_usage.append(session_api_usage)
        api_usage_total = APIUsage.merge(*api_usage)

    return dict(
        answers=answers,
        api_usage=api_usage,
        api_usage_total=api_usage_total,
    )
