import os
import streamlit.components.v1 as components
import base64

__parent_dir = os.path.dirname(os.path.abspath(__file__))
__build_dir = os.path.join(__parent_dir, "frontend/build")
__component_func = components.declare_component("RadioButtonImages", path=__build_dir)


def choose_from_images(image_paths, labels, size=200, key=None):
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
    assert len(image_paths) == len(labels)

    base64_jpgs = []
    for path in image_paths:
        with open(path, "rb") as image:
            encoded = base64.b64encode(image.read()).decode()
            base64_jpgs.append(f"data:image/jpg;base64,{encoded}")

    component_value = __component_func(base64_jpgs=base64_jpgs,
                                       labels=labels,
                                       size=size,
                                       key=key,
                                       default=0)

    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return int(component_value)
