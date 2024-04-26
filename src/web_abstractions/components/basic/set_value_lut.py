"""Here we store a look-up-table to map each basic component to its set value function
in order to be used in a generic way."""
from src.web_abstractions.components.basic.autocomplete import AutocompleteComponent
from src.web_abstractions.components.basic.dropdown import DropdownComponent
from src.web_abstractions.components.basic.input import InputComponent
from src.web_abstractions.components.basic.toggle import ToggleComponent


BASIC_COMPONENTS_SET_VALUE_LUT = {
    InputComponent: "fill",
    AutocompleteComponent: "set_value",
    DropdownComponent: "select_option",
    ToggleComponent: "toggle",
    # CheckboxComponent: "click", # Not supported yet
}
