import core
import input
import gui

if __name__ == '__main__':
    core = core.Core()
    gui = gui.Gui(core=core, debug=False)
    core.set_gui(gui)
    input = input.SensorInput(core)

    try:
        gui.mainloop()
    except KeyboardInterrupt:
        input.stop()
        core.stop()
