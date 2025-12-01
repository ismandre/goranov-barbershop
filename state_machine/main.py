from state_machine.states.state import State


class LockedState(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        if event == 'pin_entered':
            return UnlockedState()

        return self


class UnlockedState(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def on_event(self, event):
        if event == 'device_locked':
            return LockedState()

        return self


class SimpleDevice(object):
    """
    A simple state machine that mimics the functionality of a device from a
    high level.
    """

    def __init__(self):
        """ Initialize the components. """

        # Start with a default state.
        self.state = LockedState()

    def on_event(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result is
        then assigned as the new state.
        """

        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)

if __name__ == '__main__':
    device = SimpleDevice()
    device.on_event('device_locked')
    # nothing happens, state is still LockedState
    print(device.state)

    device.on_event('pin_entered')
    # state is now UnlockedState
    print(device.state)

    device.on_event('device_locked')
    # state is now LockedState again
    print(device.state)

