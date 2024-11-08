from concurrent import futures # No other edits other than title, and images so far

from .. import rel_path
from ..controller.controller import Tor

PROXY = Tor()

# if sys.platform == "win32":
#     import ctypes
#
#     myappid = __name__
#     ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
#     from ..system_proxy.__init__ import set_windows_system_proxy
#
from ..system_proxy import set_system_proxy

EXECUTOR = futures.ThreadPoolExecutor(10)

IMG_IDLE = rel_path("gui/res/gfx_mode_disabled.gif")
IMG_RUNNING = rel_path("gui/res/gfx_mode_enabled.gif")

BUTTON_DISABLED_COLOR = ("#F5F7FA", "#323133")  # 1c1c1c
BUTTON_ENABLED_COLOR = ("#FFFFFF", "#3C3B3D")  # 1c1c1c
BUTTON_BOOTSTRAPPING_COLOR = ("#323133", "#E6E9ED")


def start_gui():
    import PySimpleGUI as sg 
    sg.theme("topanga")
    ICON_BASE64 = rel_path("gui/res/app.ico")
    E_MAIN_PROGRESS_BAR = sg.ProgressBar(
        max_value=100,
        key="key",
        orientation="h",
        pad=[(0, 0), (10, 10)],
        size=(50, 10),
        bar_color=("#52df0a", "#FF0000"),
    )
    E_MAIN_BUTTON_START = sg.Button(
        "{0: ^30s}".format("Disabled"),
        key="key_button_start",
        size=(50, 1),
        pad=[(50, 50), (10, 10)],
        button_color=BUTTON_DISABLED_COLOR,
    )

    E_MAIN_IMAGE = sg.Image(
        filename=IMG_IDLE, pad=[(0, 0), (10, 10)], background_color="#FAF6F6",
    )

    L_MAIN_WINDOW_LAYOUT = [ #NGL the original person who made this has some confusing ass notes. 
        [E_MAIN_IMAGE],
        [E_MAIN_PROGRESS_BAR],
        [E_MAIN_BUTTON_START],
    ]

    P_MAIN_WINDOW = sg.Window(
        "KatSurf Anonymous v1.1",
        L_MAIN_WINDOW_LAYOUT,
        icon=ICON_BASE64,
        background_color="#FAF6F6",
        size=(320, int(320 / (5 / 3))),
        auto_size_buttons=False,
        auto_size_text=False,
        font="Terminal, 11", #ERROR!  Terminal font don't look good for this anyway
        default_button_element_size=(15, 1),
        element_padding=(0, 0),
        element_justification="center",
        text_justification="center",
        margins=(0, 0),
    )

    init = True
    while True:

        event, values = P_MAIN_WINDOW.read(50)
        if init:
            event = 'key_button_start'
            init = False

        if event != "__TIMEOUT__":
            print("event:", event)

        if event is None or event == "Exit":
            break

        if not PROXY.running:
            E_MAIN_IMAGE.update_animation(
                source=IMG_IDLE, time_between_frames=100,
            )

        elif PROXY.running:
            E_MAIN_IMAGE.update_animation(
                source=IMG_RUNNING, time_between_frames=25,
            )

        if event == "key_button_start":

            if not PROXY.running:
                # E_MAIN_BUTTON_START.update(disabled=True)

                EXECUTOR.submit(PROXY.start)

                while PROXY.status_bootstrap < 100 and not PROXY.exception:

                    P_MAIN_WINDOW.read(50)
                    x = PROXY.status_bootstrap
                    P_MAIN_WINDOW["key"].update_bar(x)
                    # P_MAIN_WINDOW["key"].update_bar(x)

                    E_MAIN_BUTTON_START.update(
                        disabled=True,
                        text="{0: ^30s}".format(f"Bootstrapping: {x} %"),
                        button_color=BUTTON_BOOTSTRAPPING_COLOR,
                        disabled_button_color=BUTTON_BOOTSTRAPPING_COLOR,
                    )

                    E_MAIN_IMAGE.update_animation(
                        source=IMG_IDLE, time_between_frames=50,
                    )
                    # time.sleep(0.005)

                    # y = x
                    # if x == 100 or PROXY.exception:
                    #     break

                E_MAIN_BUTTON_START.update(
                    disabled=True, text="Preparing Windows Proxy..."
                )

                system_proxy_isset = set_system_proxy(PROXY, enabled=True)

                _status = "Enabled | click to disable"

                if system_proxy_isset:
                    _status = "Enabled | click to disable"

                E_MAIN_BUTTON_START.update(
                    disabled=False,
                    text="{0: ^30s}".format(f"{_status}"),
                    button_color=BUTTON_ENABLED_COLOR,
                )

            elif PROXY.running:

                E_MAIN_BUTTON_START.update(
                    disabled=True,
                    button_color=BUTTON_BOOTSTRAPPING_COLOR,
                    disabled_button_color=BUTTON_BOOTSTRAPPING_COLOR,
                )
                EXECUTOR.submit(PROXY.stop)

                x = 100
                while x > 0 and not PROXY.exception:

                    P_MAIN_WINDOW.read(50)

                    x -= 5

                    E_MAIN_PROGRESS_BAR.update_bar(x)

                    E_MAIN_IMAGE.update_animation(
                        source=IMG_IDLE, time_between_frames=50,
                    )
                    E_MAIN_BUTTON_START.update(text=f"Shutting down: {x}%")

                system_proxy_isset = set_system_proxy(PROXY, False)

                if system_proxy_isset:
                    _status = "Disabled | click to enable"

                E_MAIN_BUTTON_START.update(
                    disabled=False,
                    text="{0: ^30s}".format(_status),
                    button_color=BUTTON_DISABLED_COLOR,
                )

    P_MAIN_WINDOW.close()
    return


if __name__ == "__main__":
    try:
        start_gui()
        # term background process fallback
        PROXY.process.terminate()
    except:
        raise
    finally:
        # revert proxy settings fallback
        set_system_proxy(PROXY, True)