from dataclasses import dataclass


@dataclass(frozen=True)
class APIUsage:
    name: str
    num_input_tokens: int
    num_output_tokens: int
    cost: float

    def __str__(self):
        return f"{self.name} used {self.num_input_tokens} input tokens and {self.num_output_tokens} output tokens (${self.cost:.2f})"

    @classmethod
    def merge(cls, *api_usage_reports: "APIUsage") -> "APIUsage":
        name = api_usage_reports[0].name
        total_num_input_tokens = 0
        total_num_output_tokens = 0
        total_cost = 0.
        for api_usage_report in api_usage_reports:
            assert api_usage_report.name == name, "can only merge API usages from same API"
            total_num_input_tokens += api_usage_report.num_input_tokens
            total_num_output_tokens += api_usage_report.num_output_tokens
            total_cost += api_usage_report.cost
        return APIUsage(name, total_num_input_tokens, total_num_output_tokens, total_cost)
