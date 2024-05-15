import pytest
from calmapp import app


class TestApp:
    def setup_class(self):
        self.app = app.App()

    def test_naive_run_exit(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "exit")
        assert self.app.naive_run() is None

    def test_naive_run_print(self, monkeypatch, capsys):
        input_values = ["test", "exit"]
        expected_output = ["Running app None", "To exit type 'exit'", "App: test"]

        def mock_input(_):
            return input_values.pop(0)

        monkeypatch.setattr("builtins.input", mock_input)
        self.app.naive_run()
        captured = capsys.readouterr()

        assert captured.out.splitlines() == expected_output


if __name__ == "__main__":
    pytest.main()
