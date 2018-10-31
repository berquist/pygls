##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import json
from json import JSONDecodeError

from pygls.features import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                            TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN)
from pygls.server import LanguageServer
from pygls.types import (CompletionItem, CompletionList, ConfigurationItem,
                         ConfigurationParams, Diagnostic,
                         DidChangeTextDocumentParams,
                         DidCloseTextDocumentParams, DidOpenTextDocumentParams,
                         Position, Range)


class JsonLanguageServer(LanguageServer):
    CMD_SHOW_PYTHON_PATH = "showPythonPath"

    def __init__(self):
        super().__init__()


ls = JsonLanguageServer()


def _validate(ls, params):
    text_doc = ls.workspace.get_document(params.textDocument.uri)

    diagnostics = _validate_json(text_doc)

    ls.workspace.publish_diagnostics(text_doc.uri, diagnostics)


def _validate_json(doc):
    """Validates json file."""
    diagnostics = []

    try:
        json.loads(doc.source)
    except JSONDecodeError as err:
        msg = err.msg
        col = err.colno
        line = err.lineno

        d = Diagnostic(
            Range(
                Position(line-1, col-1),
                Position(line-1, col)
            ),
            msg,
            source=type(ls).__name__
        )

        diagnostics.append(d)

    return diagnostics


@ls.feature(COMPLETION, trigger_characters=[','])
def completions(params):
    """Returns completion items."""
    return CompletionList(False, [
        CompletionItem('"'),
        CompletionItem('['),
        CompletionItem('{'),
        CompletionItem('}'),
        CompletionItem(']')
    ])


@ls.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    _validate(ls, params)


@ls.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: JsonLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.workspace.show_message("Text Document Did Close")


@ls.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.workspace.show_message("Text Document Did Open")
    ls.workspace.show_message_log("Validating json...")

    _validate(ls, params)


@ls.thread()
@ls.command(ls.CMD_SHOW_PYTHON_PATH)
def show_python_path(ls, *args):
    """Gets python path from configuration and displays it."""
    configs = ls.get_configuration(ConfigurationParams([
        ConfigurationItem("", "python")
    ])).result(1)

    python_path = None
    try:
        python_path = configs[0].pythonPath
    except Exception:
        pass

    ls.workspace.show_message("Python path: {}".format(python_path))