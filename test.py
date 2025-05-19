from Xlib import display
import subprocess
import pyatspi
import time




def main():
    def find_menubar(obj):
        if obj.getRoleName() == "menu bar":
            return obj
        for i in range(obj.childCount):
            child = obj.getChildAtIndex(i)
            result = find_menubar(child)
            if result:
                return result
        return None
    d = display.Display()
    root = d.screen().root
    NET_ACTIVE_WINDOW = d.intern_atom('_NET_ACTIVE_WINDOW')
    window_id = root.get_full_property(NET_ACTIVE_WINDOW, 0).value[0]

    window = d.create_resource_object('window', window_id)
    pid_atom = d.intern_atom('_NET_WM_PID')
    pid = window.get_full_property(pid_atom, 0).value[0]

    process_name = subprocess.check_output(['ps', '-p', str(pid), '-o', 'comm=']).decode().strip()

    print(f"[+] Active Window ID: {window_id}")
    print(f"[+] PID: {pid}")
    print(f"[+] Process: {process_name}")


    desktop = pyatspi.Registry.getDesktop(0)
    for i in range(desktop.childCount):
        app = desktop.getChildAtIndex(i)
        if app.get_process_id() == pid:
            break

    if not app:
        print("App not found in AT-SPI.")
        return []

    print(f"Found AT-SPI app: {app.name}")

    menubar = find_menubar(app)
    items = []

    if menubar:
        print(f"[+] Found menubar with {menubar.childCount} items:")
        for i in range(menubar.childCount):
            items.append(menubar.getChildAtIndex(i).name)

    return items