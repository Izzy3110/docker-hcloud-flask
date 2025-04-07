import os.path

from plyer.platforms.win.notification import instance as notification_instance


def notify(title, message, app_name=None, timeout_s=None, app_icon=None):
    if app_name is None:
        app_name = "FFmpeg Cutter"
    if timeout_s is None:
        timeout_s = 10
    if app_icon is not None and os.path.isfile(app_icon):
        notification_instance().notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=timeout_s,
            app_icon=app_icon
        )
    else:
        notification_instance().notify(
            title=title,
            message=message,
            app_name=app_name,
            timeout=timeout_s
        )
