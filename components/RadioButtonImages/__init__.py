import os
import streamlit.components.v1 as components

__parent_dir = os.path.dirname(os.path.abspath(__file__))
__build_dir = os.path.join(__parent_dir, "frontend/build")
__component_func = components.declare_component("RadioButtonImages", path=__build_dir)


def choose(caption, key=None):
    """Create a new instance of "RadioButtonImages".

    Parameters
    ----------
    images: str
        The name of the thing we're saying hello to. The component will display
        the text "Hello, {name}!"
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    int
        The number of times the component's "Click Me" button has been clicked.
        (This is the value passed to `Streamlit.setComponentValue` on the
        frontend.)
    """
    # Call through to our private component function. Arguments we pass here
    # will be sent to the frontend, where they'll be available in an "args"
    # dictionary.
    #
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.

    # convert images to base64:
    #   -> https://github.com/streamlit/streamlit/issues/1566#issue-637190487
    #   -> https://stackoverflow.com/questions/8499633/how-to-display-base64-images-in-html

    component_value = __component_func(caption=caption,
                                       key=key,
                                       default=0)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value
