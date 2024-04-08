import logging

from tenacity import after_log, before_sleep_log, retry, retry_if_exception_type, stop_after_attempt

from api_usage import APIUsage
from model import make_model
from moral_machine import Scenario, Session
from util import LogSessionStateDetailsException, UnexpectedAnswerException


class Agent:
    def __init__(self, model_name: str) -> None:
        self._model = make_model(model_name)

    @retry(
        after=after_log(logging.root, logging.WARNING),
        before_sleep=before_sleep_log(logging.root, logging.INFO),
        retry=retry_if_exception_type(UnexpectedAnswerException),
        stop=stop_after_attempt(10),
    )
    def play(self, session: Session) -> list[int]:
        self._model.reset()
        answers = []
        for scenario_idx, scenario in enumerate(session.scenarios):
            try:
                answer = self._prompt(self._make_prompt(scenario))
                if scenario.left_right_swapped:
                    answer = 1 if answer == 2 else 2
                answers.append(answer)
            except LogSessionStateDetailsException as exc:
                raise Exception(f"failed to prompt for scenario {scenario_idx}; answers so for: {answers}") from exc
        return answers

    def report_api_usage(self) -> APIUsage:
        return self._model.report_api_usage()

    def _prompt(self, prompt: str) -> int:
        result = self._model.prompt(prompt)
        if result not in {"1", "2"}:
            raise UnexpectedAnswerException(f"expected 1 or 2, got {result}")
        return int(result)

    @staticmethod
    def _make_prompt(scenario: Scenario) -> str:
        return f"1:\n{scenario.profile_left}\n\n\n\n\n2:\n{scenario.profile_right}"
