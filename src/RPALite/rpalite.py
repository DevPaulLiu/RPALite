
import random
import tempfile
import threading
import Quartz.CoreGraphics
import mss
import Quartz
from PIL import Image, ImageGrab
import numpy as np
from robot.api.deco import keyword, library, not_keyword
from robot.api import logger
from deprecated import deprecated
from pynput.mouse import Controller, Button
from pynput.keyboard import Key, Controller as KeyboardController
import time
import platform
import keyboard
import pyautogui
import pyperclip
import keyboard as keyboardlib
import cv2
from datetime import datetime
import subprocess
from image_handler import ImageHandler
import os
from functools import wraps

def windows_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if platform.system() != 'Windows':
            raise NotImplementedError(f"The {func.__name__} function is only supported on Windows.")
        return func(*args, **kwargs)
    return wrapper

@library(scope='GLOBAL', auto_keywords=True)
class RPALite:
    '''RPALite is an open source RPA (Robotic Process Automation) library. You can use RPALite via Python or Robot Framework to realize various automation tasks.
    
    Please note that the "window" or "control" in RPALite refers to a rectangle region which can be located on the system screen. The data structure is (x, y, width, height), while x is the left coordinate and y is the top coordinate of the rectangle.

    Attributes
    ----------
    debug_mode : bool
        Indicates whether the debug mode is enabled. If it is enabled, the library will output more detailed information and show some images for debugging.
    step_pause_interval : float
        The default pause interval in seconds after each step. The defaul value of this attribue is 3 seconds.    
    '''

    def __init__(self, step_pause_interval = 3, debug_mode = False, languages = ['en']):
        """
        Parameters
        ----------
        debug_mode : bool
            Indicates whether the debug mode is enabled. If it is enabled, the library will output more detailed information and show some images for debugging. The default value is False.
        
        step_pause_interval : int
            The default pause interval in seconds after each step. The defaul value of this attribue is 3 seconds.    
        
        languages : arr of str
            The languages to be used for OCR. The default value is [en'], which is English. Please refer to the language list(https://www.jaided.ai/easyocr) of EasyOCR(https://github.com/JaidedAI/EasyOCR) for more information.
        """
        self.platform = platform.system()
        self.debug_mode = debug_mode
        self.mouse_controller = Controller()
        self.keyboard_controller = KeyboardController()
        self.image_handler = ImageHandler(debug_mode, languages)
        self.step_pause_interval = step_pause_interval
        self.screen_recording_thread = None
        self.screen_recording_file = None
        

    def run_command(self, command, noblock=True):
        """
        Runs a system command. The noblock parameter specifies whether this function needs to be blocked when executing the command.
        
        Parameters
        ----------
        command : str
            The command to be executed. This can be a program file name (in the system path or full path), or any command that can be executed in the system command line.
        
        noblock : bool
            Specifies whether this function needs to be blocked when executing the command
        """
        if noblock:
            subprocess.Popen(command, shell=True)
        else:
            subprocess.run(command, shell=True, check=True)
        self.sleep()
        
        
    def sleep(self, seconds = 0):
        '''
        Sleeps for specified seconds.
           
        Parameters
        ----------
        seconds : float
            The seconds to sleep. If it is 0, the default pause interval will be used. If it is less than 0, the function will not sleep and return immediately.
        
        '''

        if(seconds == 0):
            seconds = self.step_pause_interval
        if(seconds <= 0):
            return
        else:
            time.sleep(seconds)

    def get_cursor_position(self):
        '''Gets the current mouse location. 
        
        Returns
        -------
        tuple
            A tuple of the current mouse location. The data structure is (x, y), where x is the left coordinate and y is the top coordinate of the rectangle.
        '''
        
        return pyautogui.position()


    def find_windows_by_title(self, title, image=None):
        '''
        Finds windows by a title string. This function will return all the matched windows if it exists, otherwise it will return None. A "matched window" refers to a window which are outside the text. If there are multiple windows outside the text, all windows will be returned.

        The "window" or "control" in RPALite refers to a rectangle region which can be located on the system screen. The data structure is (x, y, width, height), while x is the left coordinate and y is the top coordinate of the rectangle.
      
        Parameters
        ----------
        title : str
            A string that will be used to match the title of the window. It can only be a single line string. Text matching is essentially fuzzy matching based on OCR technology. Therefore matching is case sensitive.
        
        image : PIL image
            Indicates the image to be searched. If it is None, the function will take a screenshot of the current screen.

        Returns
        -------
        list
            A list of windows that match the title. The data structure of each window is (x, y, width, height), while x is the left coordinate and y is the top coordinate of the rectangle. Returns None if no window is found.

        '''

        if image is None:
            image = self.take_screenshot()
        text_locations = self.image_handler.find_texts_in_image(image, title)
        if text_locations is None or len(text_locations) == 0:
            return None
        else:
            rects =  []
            
            for text_location in text_locations:
                   rects += self.image_handler.find_rects_outside_position(image, text_location[0])

            return rects


    def find_control_near_text(self, text):
        '''Finds a control near a specific text. This function will return the control if it exists, otherwise it will return None.
        Please note that the "window" or "control" in RPALite refers to a rectangle region which can be located on the system screen. The data structure is (x, y, width, height), while x is the left coordinate and y is the top coordinate of the rectangle.

        Parameters
        ----------
        text : str
            A string that will be used to match the control. It can only be a single line string. Text matching is essentially fuzzy matching based on OCR technology. Therefore matching is case sensitive. 
       
        Returns
        -------
        tuple
            A tuple of the control that matches the title. The returned tuple represents the rectangle of the control. The data structure is (x, y, width, height), while x is the left coordinate and y is the top coordinate of the rectangle. Returns None if no control is found.
        '''

        img = self.take_screenshot()
        location = self.image_handler.find_texts_in_image(img, text)
        if(location is None):
            return None
        else:
            return self.image_handler.find_control_near_position(img, location[0][0])
    

    def find_control_by_label(self, label):
        '''Finds a control by the label text. This function will return the control if it exists, otherwise it will return None.
        Please note that the "window" or "control" in RPALite refers to a rectangle region which can be located on the system screen. The data structure is (x, y, width, height), while x is the left coordinate and y is the top coordinate of the rectangle.

        Parameters
        ----------
        label : str
            The label text of the control. It can only be a single line string. Text matching is essentially fuzzy matching based on OCR technology. Therefore matching is case sensitive. 
       
        Returns
        -------
        tuple
            A tuple of the control that matches the title. The returned tuple represents the rectangle of the control. The data structure is (x, y, width, height), while x is the left coordinate and y is the top coordinate of the rectangle. Returns None if no control is found.
        '''
        img = self.take_screenshot()
        location = self.image_handler.find_texts_in_image(img, label)
        if(location is None or location[0] is None):
            return None
        else:
            return self.image_handler.find_control_near_position(img, location[0][0], True)

    def get_screen_size(self):
        '''Returns the size of the screen.
        Returns
        -------
        tuple
            A tuple of (width, height) represents the width and height of the screen.
        '''
        size = pyautogui.size()
        return (size.width, size.height)

    @windows_only
    def find_control(self, app, class_name=None, title=None, automate_id=None):
        '''
        Finds a control by the parameters. This function uses uiautomation module (https://github.com/yinkaisheng/Python-UIAutomation-for-Windows) to find the control and returns the client rect of the element
        You can use ClassName, Title, automateId to search for a control. You can use Windows' Inspect tool (https://learn.microsoft.com/en-us/windows/win32/winauto/inspect-objects) or Accessibility Insights (https://accessibilityinsights.io/) to get these properties of Apps.
        In the parameters, app is mandatory. You can get the app object using 

        Parameters
        ----------
        app : 
            The application. It can be obtained by the "find_application" function.
        
        class_name : str
            The class name of the control. Use Windows Inspect tool or Accessibility Insights to find the class name of the control. 
        
        title: str  
            The title of the control. Use Windows Inspect tool or Accessibility Insights to find the title of the control.
        
        automate_id : str
            The automation ID of the control. Use Windows Inspect tool or Accessibility Insights to find the automation ID of the control.

        
        Returns
        -------
        tuple
            A tuple of the control that matches the criterias. The returned tuple represents the rectangle of the control. The data structure is (x, y, width, height), while x is the left coordinate and y is the top coordinate of the rectangle. Returns None if no control is found.
        '''

        if app is None:
            return None
        app_control = self.find_control_by_process(app.process)
        
        params = {}
       
        if(class_name is not None and class_name != ""):
            params["ClassName"] = class_name
        if(title is not None and title != ""):
            params["Name"] = title
        if(automate_id is not None and automate_id != ""):
            params["AutomationId"] = automate_id
     
        control = app_control.Control(**params)
        if control is None:
            return None
        rect = control.BoundingRectangle

        return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)

    @windows_only
    def click_control(self, app, class_name=None, title=None, automate_id=None, click_position='center', button='left', double_click=False):
        """
        Find the center, left or right position of the control then click it.

        Parameters
        ----------
        app : 
            The application. It can be obtained by the "find_application" function.
        class_name : str
            The class name of the control. Use Windows Inspect tool or Accessibility Insights to find the class name of the control. 
        title: str  
            The title of the control. Use Windows Inspect tool or Accessibility Insights to find the title of the control.
        automate_id : str
            The automation ID of the control. Use Windows Inspect tool or Accessibility Insights to find the automation ID of the control.
        click_position: str
            The position you want to click, you can use 'left','center','right'.
        button: str
            The mouse button to be clicked. Value could be 'left' or 'right'. Default is 'left'.
        double_click: bool
            Whether to perform a double click. Default is False.

        """
        position = self.find_control(app, class_name, title, automate_id)
        if click_position == 'center':
            self.click_by_position(int(position[0]) + int(position[2]) // 2, int(position[1]) + int(position[3]) // 2, button, double_click)
        if click_position == 'left':
            self.click_by_position(int(position[0]) + 5, int(position[1]) + int(position[3]) // 2, button, double_click)
        if click_position == 'right':
            self.click_by_position(int(position[0]) + (position[2]) - 5, int(position[1]) + int(position[3]) // 2, button, double_click)

    @windows_only
    def find_control_by_process(self, process_id):
        '''
        Finds an uiautomation control by the parameters. This function uses uiautomation module (https://github.com/yinkaisheng/Python-UIAutomation-for-Windows) to find the top level control based on the process_id parameter.
        Please note that the "control" here is not the control we talked about in other functions. The "control" here is the top level uiautomation control. This method is NOT a Robot Framework method. It is used by other methods which may need uiautomation library.
        
        Parameters
        ----------
        process_id : int
            The process id of the application. You can get the process id of an application with Windows Task Monitor
        
        Returns
        -------
        uiautomation control that matches the process id. Returns None if no control is found.
        
        '''
        for win in auto.GetRootControl().GetChildren():
            if win.ProcessId == process_id:
                return win
        return None   
      
    @windows_only
    def build_element_params(self, title_re=None, class_name = None, title=None, automate_id=None, visible_only= None):
        params = {}
        if(title_re is not None and title_re != ""):
            params["title_re"] = title_re
        if(class_name is not None and class_name != ""):
            params["class_name_re"] = class_name
        if(title is not None and title != ""):
            params["title"] = title
        if(automate_id is not None and automate_id != ""):
            params["auto_id"] = automate_id
        if(visible_only is not None):
            params["visible_only"] = (visible_only != False)

        return params
    
    def take_screenshot(self):
        """
        Takes a screenshot of the entire screen.
        
        Returns
        -------
        PIL.Image
            The screenshot image.
        """
        screenshot = pyautogui.screenshot()
        # note, MacOS default screenshot is 2x scale, so we need to adjust the scale factor manually.
        return self.adjust_image_scale(screenshot)
    
    def wait_until_text_shown(self, text, filter_args_in_parent=None, parent_control = None, search_in_image = None, timeout = 30):
        '''
        Wait until a specific text exists in the current screen. This function will return the location if the text exists, otherwise it will return None.
        
        Parameters
        ----------
        text : str
            The text to wait for.
            
        filter_args_in_parent : dict
            The filter arguments to filter the parent control. This is used to find the parent control of the text. If not specified, the parent control will be considered during search.
        
        parent_control : uiautomation control
            The parent control to search in. If not specified, the function will search all controls.
        
        search_in_image : PIL.Image
            The image to search in. If not specified, the function will take a screenshot and search in the screenshot.
        
        timeout : int
            The timeout in seconds. If the text is not found within the timeout, an AssertionError will be raised.

        Returns
        -------
        tuple
            The location of the text in the screen. The location is a tuple of (x, y, width, height).

        '''

        start_time = datetime.now()
        while(True):
            location = self.find_text_positions(text, filter_args_in_parent, parent_control, search_in_image)
            if(location is not None):
                return location[0] 
            else:
                diff = datetime.now() - start_time
                if(diff.seconds > timeout):
                    raise AssertionError('Timeout waiting for text: ' + text)
                self.sleep(1)
                search_in_image = None

    def wait_until_text_disppears(self, text, filter_args_in_parent=None, parent_control = None, search_in_image = None, timeout = 30):
        """
        Wait until a specific text disappears in the current screen. .

        Parameters
        ----------
        text: str
            The text that waiting to disappear.

        filter_args_in_parent : dict
            The filter arguments to filter the parent control. This is used to find the parent control of the text. If not specified, the parent control will be considered during search.
        
        parent_control : uiautomation control
            The parent control to search in. If not specified, the function will search all controls.
        
        search_in_image : PIL.Image
            The image to search in. If not specified, the function will take a screenshot and search in the screenshot.

        timeout: int
            The timeout in seconds. If the text is not disappeared within the timeout, an AssertionError will be raised.

        """
        start_time = datetime.now()
        while(True):
            disappear_text= self.find_text_positions(text, filter_args_in_parent, parent_control, search_in_image)
            if disappear_text is None:
                return
            else:
                diff = datetime.now() - start_time
                if diff.seconds > timeout:
                    raise AssertionError('Timeout waiting for text disappears: ' + text)
                self.sleep(1)
                search_in_image = None

    def validate_text_exists(self, text, filter_args_in_parent=None, parent_control = None, img = None, throw_exception_when_failed = True):
        '''Validate if a specific text exists in the current screen. If the text exists, this function will return the position of the text; otherwise it will raise an AssertionError.
        
        Parameters
        ----------
        text : str
            The text to search for.
        
        filter_args_in_parent : dict
            The filter arguments to filter the parent control. This is used to find the parent control of the text. If not specified, the parent control will be considered during search.
        
        parent_control : uiautomation control
            The parent control to search in. If not specified, the function will search all controls.
        
        img : PIL.Image
            The image to search in. If not specified, the function will take a screenshot and search in the screenshot.
        
        throw_exception_when_failed : bool = True
            Whether to raise an AssertionError when the text is not found. If set to False, this function will return None if the text is not found.
            
        Returns
        -------
        tuple
            The location of the text in the screen. The location is a tuple of (x, y, width, height). Please note that the function will raise an AssertionError if the text does not exist.

        '''
        if not text and throw_exception_when_failed:
            raise AssertionError('Text cannot be empty.')
        if not text:
            return None
        position = self.find_text_positions(text, filter_args_in_parent, parent_control, img, True)
        
        if not position:
            raise AssertionError('Text not found: ' + text)
        return position
    
    def find_text_positions(self, text, filter_args_in_parent=None, parent_control = None, img = None, exact_match=False):
        '''Find a text in the current screen. This function will return the location if the text exists, otherwise it will return None.
        
        Parameters
        ----------
        text : str
            The text to search for.
        
        filter_args_in_parent : dict
            The filter arguments to filter the parent control. This is used to find the parent control of the text. If not specified, the parent control will be considered during search.
        
        parent_control : uiautomation control
            The parent control to search in. If not specified, the function will search all controls.

        img : PIL.Image
            The image to search in. If not specified, the function will take a screenshot and search in the screenshot.
        
        Returns
        -------
        tuple
            The location of the text in the screen. The location is a tuple of (x, y, width, height).
        '''
        if img is None:
            img = self.take_screenshot()
        
        locations = self.image_handler.find_texts_in_rects(img, text, filter_args_in_parent, parent_control)
        if(locations is None or len(locations) == 0):
            return None
        elif exact_match and (len(locations[0]) < 2 or (not locations[0][1]) or (not (locations[0][1] in text) and not (text in locations[0][1]))):
            return None
        else:
            return [loc[0] for loc in locations]

    @windows_only
    def find_application(self, title=None, class_name = None):
        '''Find an application by its title or ClassName.'''

        if title is None and class_name is None:
            raise Exception('Either title or class name must be specified.')
        params = self.build_element_params(title, class_name)
    
        windows = findwindows.find_elements(**params)
        if(len(windows) == 0):
            return None
        else:
            process_id = windows[0].process_id
            return Application().connect(process = process_id)

    @not_keyword
    def get_app(self, app_or_keyword):
        app = app_or_keyword
        if(type(app_or_keyword) == str):
            app = self.find_application(app_or_keyword, None)
        return app

    @windows_only
    def close_app(self, app_or_keyword, force_quit = False):
        '''Close an application. The parameter could be the app instance or the app's title keyword. The force_quit parameter specify whether this function need to be forced quit just like what we did in task manager.'''
        app = self.get_app(app_or_keyword)
        if(app is None):
            pass
        else:
            app.kill(not(force_quit))

    @windows_only
    def maximize_window(self, app_or_keyword, window_title_pattern = None):
        '''Maximize the window of the application.'''
        app = self.get_app(app_or_keyword)

        window = None

        if window_title_pattern is not None:
            window = app.window(found_index=0, title_re=window_title_pattern)
        elif app.window() is not None:
            window = app.window(found_index=0)
        
        if window is not None:
            wrapper = window.wrapper_object()
            wrapper.maximize()
            self.sleep()

    @windows_only
    def locate(self, location_description, parent_image = None, app = None):
        ''' Locate a control by a description. The description can be a string that is displayed on screen or a string of some elements' properties with a prefix.
        This function will work based on location_description's value based on these rules:
            - If the description starts with "image:", the function will try to load the image file based on the path after "image:". Then it will search for the image and return the location.
            - If the description starts with "automateId:", the function will try to find the control by the automation id and return the location of the control.
            - If the description doesn't start with any prefix, the function will try to find the control by the text and return the location of the matched text.

        Parameters
        ----------
        location_description : str
            The description of the control. The description can be a string that is displayed on screen or a string of some elements' properties with a prefix. 
        
        parent_image : PIL.Image
            The image to search in. If not specified, the function will take a screenshot and search in the screenshot.

        app : Application
            The application to search in. If not specified, the function will search in the current application. See find_application() for more information.
        
        Returns
        -------
        tuple
            The location of the control. The location is a tuple of (x, y, width, height).
    
        '''
        
        if(isinstance(location_description, str)):
            if location_description.startswith('image:'):
                path = location_description.split('image:')[1]
                img = Image.open(path)
                if parent_image is None:
                    parent_image = self.take_screenshot()
                return self.image_handler.find_image_location(img, parent_image)
            
            if location_description.startswith('automateId:'):
                automate_id = location_description.split('automateId:')[1]
                logger.debug('Clicking by automate id:', automate_id)
                if app is None:
                    logger.error('App is not specified. Return None')
                    return None
                position = self.find_control(app, automate_id=automate_id)
                return position
             
            return self.wait_until_text_shown(location_description)

    def click(self, locator=None,  button='left', double_click= False, app = None):
        '''Click on a control. The parameter could be a locator or the control's text (like the button text or the field name)'''
        if locator is None:
            position = self.get_cursor_position()
            self.click_by_position(position[0], position[1], button, double_click)

        if(isinstance(locator, str)):
            if locator.startswith('automateId:'):
                if(app is None):
                    logger.error('App is not specified for automateId click. Cancel clicking')
                    raise AssertionError('App is not specified for automateId click. Cancel clicking')
        
            position = self.locate(locator, app=app)

            if position is None:
                return
                    
            self.click_by_position(position[0] + int(position[2]/2), position[1] + int(position[3]/2), button, double_click)          
         
        pass

    def click_by_image(self, image, button='left', double_click= False):
        '''Click center position of an image in the parent image or the entire screen if no parent image is provided.
        Parameters
        ----------     
        image: str or PIL image
            The image to search for. This can be the path of image or PIL image.

        button: str
            The mouse button to be clicked. Value could be 'left' or 'right'. Default is 'left'

        double_click: bool
            Whether to perform a double click. Default is False.
        '''         
        location = self.find_image_location(image)
        if(location is not None):
            self.click_by_position(int(location[0]) + int(location[2]) // 2, int(location[1]) + int(location[3]) // 2, button, double_click)

    def find_image_on_screen(self, image):
        '''Find an image in the current screen. This function will return the location if the image exists, otherwise it will return None.
        
        Parameters
        ----------
        image: str or PIL image
            The image to search for in current screen. 
        
        Returns
        -------
        tuple
            The location of the image in the screen. The location is a tuple of (x, y, width, height).
        '''
        return self.find_image_location(image)

    def find_image_location(self, image, parent_image = None):
        '''Find an image in the parent image or the entire screen if no parent image is provided. This function will return the location if the image exists, otherwise it will return None.
        
        Parameters
        ----------
        image: str or PIL image
            The image to search for. This can be the path of image or PIL image.

        parent_image: str or PIL image
            The image to search from. This can be the path of image or PIL image.

        Returns
        -------
        tuple
            The location of the image in the screen. The location is a tuple of (x, y, width, height).
        '''
        if isinstance(image, str):
            image = self.adjust_image_scale(Image.open(image))
        if parent_image is None:
            parent_image = self.take_screenshot()
        elif isinstance(parent_image, str):
            parent_image = self.adjust_image_scale(Image.open(parent_image))

        return self.image_handler.find_image_location(image, parent_image)
    
    def find_all_image_locations(self, image, parent_image = None):
        '''Find all images in the parent image or the entire screen if no parent image is provided. This function will return the locations if the image exists, otherwise it will return None.
        
        Parameters
        ----------
        image: str or PIL image
            The image to search for. This can be the path of image or PIL image.

        parent_image: str or PIL image
            The image to search from. This can be the path of image or PIL image.

        Returns
        -------
        list
            A list of locations of the image in the screen. Each location is a tuple of (x, y, width, height).
        '''
        if isinstance(image, str):
            image = self.adjust_image_scale(Image.open(image))
        if parent_image is None:
            parent_image = self.take_screenshot()
        elif isinstance(parent_image, str):
            parent_image = self.adjust_image_scale(Image.open(parent_image))

        return self.image_handler.find_all_image_locations(image, parent_image)

    def wait_until_image_shown(self, image, parent_image = None, timeout = 30):
        '''
        Parameters
        ----------
        image: str or PIL image
            The image to search for. This can be the path of image or PIL image.

        parent_image: str or PIL image
            The image to search from. This can be the path of image or PIL image.

        Returns
        -------
        tuple
            The location of the image in the screen. The location is a tuple of (x, y, width, height).
        '''
        start_time = datetime.now()
        while(True):
            location = self.find_image_location(image, parent_image)
            if(location is not None):
                return location 
            else:
                diff = datetime.now() - start_time
                if(diff.seconds > timeout):
                    raise AssertionError('Timeout waiting for image')
                self.sleep(1)
            return location

    def click_by_text_inside_window(self, text, window_title, button='left', double_click= False):
        '''Click the positon of a string on screen. '''
        logger.debug('Click by text inside window:' + text + " window title: " + window_title)
        img = self.take_screenshot()
        window_title_positions = self.image_handler.find_texts_in_image(img, window_title)
        if(window_title_positions is None or len(window_title_positions) == 0):
            logger.error('Cannot find window title: ' + window_title)
            return
        title_position = window_title_positions[0][0]

        rects = self.find_windows_by_title(window_title, img)
        if(rects is None or len(rects) ==0):
            return None
        else:
            locations = self.find_text_positions(text, None, rects, img)
            if locations is None or len(locations) == 0:
                logger.error('Cannot find text: ' + text + ' in window: ' + window_title)
                return

            if locations is not None and len(locations) > 1:
                sorted_locations = sorted(locations, key=lambda x: (x[0]-title_position[0])**2 + (x[1]-title_position[1])**2)
            else:
                sorted_locations = [locations]
            location = sorted_locations[0]
            self.click_by_position(location[0], location[1], button, double_click)
            self.sleep()
        self.sleep()

    def click_by_text(self, text, button='left', double_click=False, filter_args_in_parent=None):
        '''
        Clicks the center position of a string on screen. 
        '''
        logger.debug('Click by text:', text)
        location = self.wait_until_text_shown(text, filter_args_in_parent)
        if(location is not None and location[0]):
            self.click_by_position(int(location[0]) + int(location[2]) // 2, int(location[1]) + int(location[3]) // 2, button, double_click)
        self.sleep()


    def mouse_press(self, button='left'):
        '''Presses the mouse button.

        Parameters:
        ----------
        button: str
            The mouse button to be pressed. Value could be 'left' or 'right'. Default is 'left'
        '''
        pyautogui.mouseDown(button=button)

    def mouse_release(self, button='left'):
        '''Releases the mouse button. 

        Parameters:
        ----------
        button: str
            The mouse button to be released. Value could be 'left' or 'right'. Default is 'left'
        '''
        pyautogui.mouseUp(button=button)

    def copy_text_to_clipboard(self, text):
        '''
        Copy the text to the clipboard.

        Parameters:
        ----------
        text: str
            The text to be copied to the clipboard.
        '''
        pyperclip.copy(text)

    def get_clipboard_text(self):
        '''
        Returns the text in the clipboard.
        '''
        return pyperclip.paste()


    def scroll(self, times = 1, sleep = None):
        '''
        Scrolls the mouse wheel. 
        
        Parameters:
        ----------
        times: int
            The number of times to scroll the wheel. Default is 1. This parameter also indicates the scroll direction. Positive value means scrolling up, and negative value means scrolling down. 
        
        sleep: float
            The time to sleep in seconds after scrolling. 
        '''
        if platform.system() == 'Darwin':
            pyautogui.scroll(-times)
        else: 
            pyautogui.scroll(times)
        sleep_seconds = sleep if sleep is not None else self.step_pause_interval
        self.sleep(sleep_seconds)
        pass

    def mouse_move(self, x:int, y:int):
        self.mouse_controller.position = (x, y)
        self.sleep()
    
    def mouse_click(self, x: int, y: int, button='left', double_click=False):
        '''
        Perform a single click at the specified position.
        '''
        # Map button string to pynput Button
        button_map = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }
        pynput_button = button_map.get(button, Button.left)

        # Move to the position before clicking
        self.mouse_controller.position = (x, y)
        self.sleep()
        if double_click:
            self.mouse_controller.click(pynput_button, 2)
        else:
            self.mouse_controller.click(pynput_button)  # Single click
        self.sleep()
        
    def move_mouse_to_the_middle_of_text(self, text, filter_args_in_parent=None, parent_control=None, search_in_image=None, timeout=30):
        '''
        Move mouse to the center position of a string on screen. 
        '''
        position = self.wait_until_text_shown(text, filter_args_in_parent, parent_control, search_in_image, timeout)
        self.mouse_move(int(position[0]) + int(position[2]) // 2, int(position[1]) + int(position[3]) // 2)

    def click_by_position(self, x:int, y:int, button='left', double_click=False):
        '''
        Clicks the positon based on the coordinates. Please note that this function will perform these steps:
        1. Move the mouse to the position
        2. Wait for 1 second
        3. Click the mouse

        Parameters:
        ----------
        x: int
            The x coordinate of the position to be clicked

        y: int
            The y coordinate of the position to be clicked

        button: str
            The mouse button to be clicked. Value could be 'left' or 'right'. Default is 'left'

        double_click: bool
            Whether to perform a double click. Default is False.
        '''
        logger.debug('Click by position: {}, {}, {}, {}'.format(x, y, type(x), type(y)))
        self.mouse_click(x, y, button, double_click)
        self.sleep()

    def send_keys(self, shortcut):
        '''
        Simulate the keyboard action to send shortcuts.

        Parameters
        ----------
        shortcut : str
            The shortcut to be sent. E.g., 'ctrl+c', 'command+3', 'shift+a'
        '''
        key_map = {
            'ctrl': Key.ctrl,
            '^': Key.ctrl,
            'shift': Key.shift,
            '+': Key.shift,
            'alt': Key.alt,
            '%': Key.alt,
            'cmd': Key.cmd if self.platform == 'Darwin' else Key.cmd_l,
            'command': Key.cmd if self.platform == 'Darwin' else Key.cmd_l,
            'enter': Key.enter,
            'tab': Key.tab,
            'esc': Key.esc,
            'space': Key.space,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
        }

        keys = shortcut.lower().split('+')
        with self.keyboard_controller.pressed(*[key_map.get(k, k) for k in keys]):
            self.sleep()


    def input_text(self, text, seconds = 0):
        '''
        Types text at the current active position.
        This function is an automation method and will not return any value.

        Parameters
        ----------
        text : str
            Text to type
        '''
        self.keyboard_controller.type(text)
        self.sleep(seconds)

    def get_text_field_value(self, field_name):
        '''
        Returns the text value of a text field identified by field_name parameter.

        Parameters
        ----------
        field_name : str
            Label or name of the field to get text from
        '''
        img = self.take_screenshot()
        location = self.find_control_by_label(field_name)
        if(location is None):
            logger.error('Cannot find field:', field_name)
            return ''
        text_arr = self.image_handler.find_texts_inside_rect(img, field_name, location)
        result = ''
        current_y = 999999
        for i, (location, target_text) in enumerate(text_arr):
            if(location[1] < current_y):
                if i > 0:
                    target_text = ' ' + target_text    
                result +=  target_text 
                
                current_y = location[1] + location[3]
            else:
                result += '\n' + target_text
            
        return result

    def enter_in_field(self, field_name, text):
        '''
        Enters text in a field identified by field_name paramete.
        This function is an automation method and will not return any value.

        Parameters
        ----------
        field_name : str
            Label or name of the field to enter text in
        
        text : str
            Text to enter in the field
    
        '''
        img = self.take_screenshot()
        location = self.wait_until_text_shown(field_name)
        if(location is None):
            logger.error('Cannot find field:', field_name)
            return
        (x,y,w,h) = self.image_handler.find_control_near_position(img, location, True)
        self.click_by_position(x+3, y+3)
        self.input_text(text)
        self.sleep()

    def start_screen_recording(self, target_avi_file_path = None, fps = 10):
        '''
        Starts recording the screen.
        This function is an automation method and will not return any value.

        Parameters
        ----------
        target_avi_file_path : str
            File name to save the video file. If this value is set to None, RPALite will create a file in the temp folder with a random name
        fps : int
            Frame per second, default is 10
        '''
        if target_avi_file_path is None or target_avi_file_path == '':
            temp_dir = tempfile.mkdtemp()
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            target_avi_file_path = os.path.join(temp_dir, str(random.randint(10000, 99999)) + '.avi')
        thread = threading.Thread(target=self.record_screen_impl, args=(target_avi_file_path, fps))
        thread.start()
        self.screen_recording_thread = thread
        return target_avi_file_path

    def stop_screen_recording(self):
        '''
        Stops recording the screen.
        This function is an automation method and will not return any value.
        '''
        if self.screen_recording_thread:
            self.screen_recording_thread.keep_recording = False
        self.screen_recording_thread = None
        recording_file = self.screen_recording_file + ''
        self.screen_recording_file = None
        return recording_file

    @not_keyword
    def record_screen_impl(self, target_avi_file_path, fps = 10):
        '''
        Recording the screen.
        This function is an automation method and will not return any value.

        Parameters
        ----------
        target_avi_file_path : str
            The target AVI file path to save the video file
        
        fps : int
            Frame per second, default is 10
        '''
        screen_size = self.get_screen_size()
        
        # Specify video codec
        codec = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(target_avi_file_path, codec, fps, screen_size)

        self.keep_screen_recording = True
        t = threading.currentThread()
        self.screen_recording_file = target_avi_file_path
        # X and Y coordinates of mouse pointer
        Xs = [0,8,6,14,12,4,2,0]
        Ys = [0,2,4,12,14,6,8,0]

        while getattr(t, "keep_recording", True):
            img = pyautogui.screenshot()
          

            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      

            out.write(frame)

        # Release the Video writer
        out.release()
    
    @not_keyword
    def adjust_image_scale(self, image):
        '''
        Adjusts the scale of the image based on the screen's scale factor.
        
        Parameters
        ----------
        image : PIL.Image
            The image to be adjusted.
        
        Returns
        -------
        PIL.Image
            The adjusted image.
        '''
        scale_factor = self.get_scale_factor()
        if scale_factor > 1:
            width, height = image.size
            image = image.resize((int(width / scale_factor), int(height / scale_factor)), Image.Resampling.LANCZOS)
        return image
    
    def show_desktop(self):
        '''
        Shows desktop and minimizes all windows.
        '''
        if self.platform == 'Windows':
            self.keyboard_controller.press(Key.cmd)
            self.keyboard_controller.press('d')
            self.keyboard_controller.release('d')
            self.keyboard_controller.release(Key.cmd)
        elif self.platform == 'Linux':
            self.keyboard_controller.press(Key.cmd)
            self.keyboard_controller.press('d')
            self.keyboard_controller.release('d')
            self.keyboard_controller.release(Key.cmd)
        elif self.platform == 'Darwin':
            self.keyboard_controller.press(Key.cmd)
            self.keyboard_controller.press(Key.alt)
            self.keyboard_controller.press('h')
            self.keyboard_controller.release('h')
            self.keyboard_controller.release(Key.alt)
            self.keyboard_controller.press(Key.cmd)
            self.keyboard_controller.press('m')
            self.keyboard_controller.release('m')
            self.keyboard_controller.release(Key.cmd)

    @not_keyword
    def get_scale_factor(self):
            '''
            Returns the scale factor of the screen.
            '''
            if self.platform == "Darwin":
                display_id = Quartz.CGMainDisplayID()
                screen = Quartz.CGDisplayScreenSize(display_id)
                pixel_width = Quartz.CGDisplayPixelsWide(display_id)
                scale_factor = pixel_width / screen.width
                return min(scale_factor, 2)
            return 1