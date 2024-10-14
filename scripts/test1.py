#!/usr/bin/python3
'''sd-webui-aspect_ratios-dd
Extension for AUTOMATIC1111.

Version 0.0.0.6

Description
The aspect ratios are given in a list. From this list a dictionary 
is created, in which e.g. the key is "1:1" and the value is 1.0. This
dictionary is required in my approach to get the value on base of the 
key.
'''
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=attribute-defined-outside-init
# pylint: disable=import-error
# pylint: disable=consider-using-from-import
# pylint: disable=trailing-whitespace
# pylint: disable=unused-argument
# pylint: disable=too-many-instance-attributes
# pylint: disable=no-self-use
# pylint: disable=bad-indentation
# pylint: disable=unused-variable

# Import the Python modules.
import contextlib
import gradio as gr
import modules.scripts as scripts
from modules.ui_components import ToolButton, InputAccordion
from pathlib import Path

# Define module variables.
_width = 512
_height = 512

# Define the data paths.
extension_data_path = "extension_data/aspect_ratio.data"
user_data_path = "user_data/aspect_ratio.data"

# Get the base path.
BASE_PATH = scripts.basedir()

# Create the paths.
fn_data = Path(BASE_PATH, extension_data_path)
fn_user = Path(BASE_PATH, user_data_path)

# Check if files exist.
if Path(fn_user).is_file():
    pass
elif Path(fn_data).is_file():   
    arlist = []
    # Open file for reading.
    with open(fn) as f:
        # Read each line in the file
        for line in f:
            data = line.strip()      
            arlist.append(data)      

# Create a dictionary.
ardict = dict()
for ele in arlist:
    try:      
        templist = ele.split(":")
        fval = float(templist[0]) / float(templist[1])       
        ardict[str(ele)] = fval 
    except:
        print("*** Could not parse: " + str(ele))      

# Define class ARDDButton.
class  ARDDButton(ToolButton):
    '''New button class.'''
    def __init__(self, **kwargs):
        '''Class init method.'''
        super().__init__(**kwargs)

    def apply(self, ar, w, h):
        '''Class method apply.'''
        # Initialise height and width.
        w = _width
        h = _height
        # Calculate new width and height.
        if ar > 1.0:  # fixed height, change width
            w = ar * h
        elif ar < 1.0:  # fixed width, change height
            h = w / ar
        else:  # set minimum dimension to both
            min_dim = min([w, h])
            w, h = min_dim, min_dim
        # Create a new list.
        retlst = list(map(round, [w, h]))
        # Return the list with width and height.
        return retlst

# Define class ARDDScript.
class ARDDScript(scripts.Script):
    '''Class for selecting the aspect ratio.'''
    
    def title(self):
        '''Class method title.'''
        return "Aspect Ratio Selector"

    def show(self, is_img2img):
        '''Class method show.'''
        return scripts.AlwaysVisible  # hide this script in the Scripts dropdown

    def image_resolution(self, is_img2img):
        '''Get the image resolution from container and return the values.'''
        if is_img2img:
            imgres = [self.i2i_w, self.i2i_h]
        else:
            imgres = [self.t2i_w, self.t2i_h]
        return imgres    

    def ui(self, is_img2img):
        '''Class method ui.'''
        # Set the css format strings.
        css_acc = f'{"img" if is_img2img else "txt"}2img_ARDD_accordion_aspect_ratio' 
        css_col = f'{"img" if is_img2img else "txt"}2img_ARDD_column_aspect_ratio'
        css_row = f'{"img" if is_img2img else "txt"}2img_ARDD_row_aspect_ratio'
        # Create a column.
        with gr.Column(elem_id=css_col):
            with InputAccordion(value=False,
                label="Common Landscape Aspect Ratios", 
                elem_id=css_acc
            ) as enabled:
                with gr.Row(elem_id=css_row):      
                    arval = gr.Dropdown(arlist, label="Aspect Ratios", value="1:1")
                    exact = gr.Textbox(value="EXACT", lines=1, render=True,
                            interactive=True, label="Calculation of Width/Height")
                with gr.Row(elem_id=css_row):
                    rst = ARDDButton(value="Reset")
                    btn = ARDDButton(value="Apply")
                    chg = ARDDButton(value="Change Orientation")
                    with contextlib.suppress(AttributeError):
                        imgres = self.image_resolution(is_img2img)
                        def update_button(arstr):
                            #btn.ar = ardict[arstr]
                            ar = ardict[arstr]
                            return btn.apply(ar, _width, _height)
                        def check_calc(arstr):    
                            retval = "ROUNDED"      
                            ar = ardict[arstr]
                            x = _width
                            y = x * ar
                            print(x, y)      
                            if float(y).is_integer():
                                retval = "EXACT"        
                            return retval          
                        btn.click(update_button, inputs=[arval], outputs=imgres)
                        btn.click(check_calc, inputs=[arval], outputs=exact)      
                        def update_rst0(arstr): 
                            #rst.ar = 1.0  # not so good. rework.
                            return rst.apply(ar, _width, _height)
                        def update_rst1(arstr): 
                            rst = "1:1"
                            return rst
                        rst.click(update_rst0, inputs=[arval], outputs=imgres)
                        rst.click(update_rst1, inputs=[arval], outputs=[arval])
                        def update_chg(arstr):
                            #chg.ar = 1/ardict[arstr]  # not so good. rework.
                            ar = 1/ardict[arstr] 
                            return chg.apply(ar, _width, _height)
                        chg.click(update_chg, inputs=[arval], outputs=imgres)
                              
    # Class method after_component.
    def after_component(self, component, **kwargs):
        '''Class method after_component.

        This method is used to generalize the existing code. It is detected if 
        one is in the txt2img tab or the img2img tab. Then the corresponding self
        variables can be used in the same code for both tabs.
        '''
        if kwargs.get("elem_id") == "txt2img_width":
            self.t2i_w = component
        if kwargs.get("elem_id") == "txt2img_height":
            self.t2i_h = component
        if kwargs.get("elem_id") == "img2img_width":
            self.i2i_w = component
        if kwargs.get("elem_id") == "img2img_height":
            self.i2i_h = component
        if kwargs.get("elem_id") == "img2img_image":
            self.image = [component]
        if kwargs.get("elem_id") == "img2img_sketch":
            self.image.append(component)
        if kwargs.get("elem_id") == "img2maskimg":
            self.image.append(component)
        if kwargs.get("elem_id") == "inpaint_sketch":
            self.image.append(component)
        if kwargs.get("elem_id") == "img_inpaint_base":
            self.image.append(component)
