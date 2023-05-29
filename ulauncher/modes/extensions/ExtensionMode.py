import html

from ulauncher.api.result import Result
from ulauncher.api.shared.action.BaseAction import BaseAction
from ulauncher.api.shared.event import LaunchTriggerEvent
from ulauncher.api.shared.query import Query
from ulauncher.modes.BaseMode import BaseMode
from ulauncher.modes.extensions.DeferredResultRenderer import DeferredResultRenderer
from ulauncher.modes.extensions.ExtensionServer import ExtensionServer


# bind function to args, ignoring further args on call time
def bind_final(fn, *args):
    return lambda *_: fn(*args)


class ExtensionMode(BaseMode):
    def __init__(self):
        self.extensionServer = ExtensionServer.get_instance()
        self.deferredResultRenderer = DeferredResultRenderer.get_instance()

    def is_enabled(self, query: Query):
        return bool(self.extensionServer.get_controller_by_keyword(query.keyword)) and " " in query

    def on_query_change(self, _query: Query):
        """
        Triggered when user changes the query
        """
        self.deferredResultRenderer.on_query_change()

    def handle_query(self, query: Query) -> BaseAction:
        controller = self.extensionServer.get_controller_by_keyword(query.keyword)

        if not controller:
            msg = "Invalid extension keyword"
            raise RuntimeError(msg)

        return controller.handle_query(query)

    def get_triggers(self):
        """
        :rtype: Iterable[:class:`~ulauncher.api.result.Result`]
        """
        for controller in self.extensionServer.controllers.values():
            for trigger_id, trigger in controller.manifest.triggers.items():
                action = None
                if trigger.keyword is None:
                    action = bind_final(controller.trigger_event, LaunchTriggerEvent(trigger_id))
                elif trigger.user_keyword:
                    action = f"{trigger.user_keyword} "

                if action:
                    yield Result(
                        name=html.escape(trigger.name),
                        description=html.escape(trigger.description),
                        icon=controller.get_normalized_icon_path(trigger.icon),
                        on_enter=action,
                        searchable=True,
                    )
