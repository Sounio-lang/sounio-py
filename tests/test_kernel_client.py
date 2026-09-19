from queue import Empty
from unittest.mock import Mock

import pytest
from sounio.kernel_client import KernelConnection


def message(kind, content, parent='current'):
    return {'msg_type': kind, 'content': content, 'parent_header': {'msg_id': parent}}


def connection(messages):
    client = Mock()
    client.execute.return_value = 'current'
    client.get_shell_msg.return_value = message('execute_reply', {'status': 'ok'})
    client.get_iopub_msg.side_effect = messages
    return KernelConnection(Mock(), client)


def test_outputs_and_idle_from_other_requests_are_ignored():
    kernel = connection([
        message('stream', {'name': 'stdout', 'text': 'unrelated'}, 'old'),
        message('status', {'execution_state': 'idle'}, 'old'),
        message('stream', {'name': 'stdout', 'text': 'correct'}),
        message('status', {'execution_state': 'idle'}),
    ])
    result = kernel.execute('source')
    assert result.ok
    assert result.stdout == 'correct'


def test_timeout_is_not_success():
    with pytest.raises(TimeoutError):
        connection([Empty()]).execute('source')


def test_transport_error_is_not_success():
    with pytest.raises(ConnectionError):
        connection([ConnectionError('disconnected')]).execute('source')


def test_error_output_retains_failed_status():
    kernel = connection([
        message('error', {'traceback': ['\x1b[31mrejected\x1b[0m']}),
        message('status', {'execution_state': 'idle'}),
    ])
    result = kernel.execute('source')
    assert not result.ok
    assert result.stderr == 'rejected'


def test_shell_reply_error_is_not_hidden_by_idle():
    kernel = connection([message('status', {'execution_state': 'idle'})])
    kernel._kc.get_shell_msg.return_value = message('execute_reply', {'status': 'error'})
    assert not kernel.execute('invalid').ok
