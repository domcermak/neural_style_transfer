import {
    Streamlit,
    StreamlitComponentBase,
    withStreamlitConnection,
} from "streamlit-component-lib"
import React, {ReactNode} from "react"

class RadioButtonImages extends StreamlitComponentBase {
    public state = {numClicks: 0, isFocused: false}

    public render = (): ReactNode => {
        const images = this.props.args["base64_jpgs"]
        const labels = this.props.args["labels"]
        const size = this.props.args["size"]

        const defaultCheckedIdx = '0';
        Streamlit.setComponentValue(defaultCheckedIdx);

        return (
            <div className="button-set-container">
                {Object.keys(images).map((idx) => (
                    <div>
                        <input id={idx} type="radio" name="image" value={idx} defaultChecked={idx === defaultCheckedIdx}
                               onChange={(e) => {
                                   if (e.target.value === idx) {
                                       Streamlit.setComponentValue(idx)
                                   }
                               }}/>
                        <label htmlFor={idx}>
                            <img src={images[idx]} height={size + "px"} width={size + "px"} alt={labels[idx]}/>
                            <svg className="checkmark" version="1.1" viewBox="0 0 288 288"
                                 xmlns="http://www.w3.org/2000/svg">
                                <circle transform="matrix(.7916 0 0 .7916 30.01 30.01)" cx="144" cy="144" r="144"
                                        fill="#fff"/>
                                <g transform="matrix(.83 0 0 .83 24.48 24.48)">
                                    <svg width="288" height="288" enableBackground="new 0 0 122.88 122.88"
                                         viewBox="0 0 122.88 122.88" xmlns="http://www.w3.org/2000/svg">
                                        <path className="color000 svgShape"
                                              d="m61.44 0c33.932 0 61.44 27.508 61.44 61.44s-27.508 61.439-61.44 61.439c-33.933 1e-3 -61.44-27.507-61.44-61.439s27.507-61.44 61.44-61.44zm-27.182 63.075c0.824-4.78 6.28-7.44 10.584-4.851 0.39 0.233 0.763 0.51 1.11 0.827l0.034 0.032c1.932 1.852 4.096 3.778 6.242 5.688l1.841 1.652 21.84-22.91c1.304-1.366 2.259-2.25 4.216-2.689 6.701-1.478 11.412 6.712 6.663 11.719l-27.223 28.565c-2.564 2.735-7.147 2.985-9.901 0.373-1.581-1.466-3.297-2.958-5.034-4.467-3.007-2.613-6.077-5.28-8.577-7.919-1.502-1.5-2.15-3.956-1.795-6.02z"
                                              clipRule="evenodd" fillRule="evenodd"/>
                                    </svg>
                                </g>
                            </svg>
                        </label>
                    </div>
                ))}
            </div>
        )
    }
}

export default withStreamlitConnection(RadioButtonImages)
