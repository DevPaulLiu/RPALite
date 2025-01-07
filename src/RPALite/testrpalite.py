import sys
from rpalite import RPALite

# Initialize RPALite instance
rpalite = RPALite(debug_mode=False)

# verified passed functions
# rpalite.show_desktop()
# rpalite.mouse_move(10, 10)
# rpalite.move_mouse_to_the_middle_of_text('Terminal')
# rpalite.mouse_click(20, 10, button='left')
# rpalite.mouse_click(30, 10, button='left', double_click=True)
# rpalite.mouse_press(button='right')
# rpalite.mouse_release(button='right')
# rpalite.scroll(times=1)
# rpalite.click_by_position(40, 10, button='left', double_click=False)
# rpalite.click_by_position(50, 10, button='left', double_click=True)
# print(rpalite.get_cursor_position())
# print(rpalite.get_text_field_value('To:'))
# rpalite.run_command('open -a Safari', noblock=True)
# rpalite.sleep(1)

# reacts = rpalite.find_windows_by_title('README.md')
# position = reacts[0]
# rpalite.click_by_position(position[0], position[1], button='left', double_click=True)
# rpalite.click_by_position(position[0], position[1])
# print(rpalite.get_screen_size())
# screenshot = rpalite.take_screenshot()
# print(rpalite.wait_until_text_shown('OUTLINE'))
# rpalite.wait_until_text_disppears('Code')
# print(rpalite.validate_text_exists('CALL STACK'))
# rpalite.click('File')
# rpalite.click_by_text('Edit')
# rpalite.click_by_text_inside_window('MainPage.xaml', 'Solution')

# print(rpalite.find_image_on_screen('/Users/xamltest/Desktop/rpalite/src/test.png'))
# print(rpalite.find_image_location('/Users/xamltest/Desktop/rpalite/src/test2.png'))
# rpalite.click_by_image('/Users/xamltest/Desktop/rpalite/src/test.png')
# rpalite.click_by_image('/Users/xamltest/Desktop/rpalite/src/test2.png')
# x = rpalite.wait_until_image_shown('/Users/xamltest/Desktop/rpalite/src/test3.png')
# rpalite.click_by_position(x[0], x[1])
#print(rpalite.find_all_image_locations('/Users/xamltest/Desktop/rpalite/src/test4.png'))


# rpalite.input_text('Hello, World!')
# rpalite.enter_in_field('Password', 'test_user')
# rpalite.copy_text_to_clipboard('Hello, World!')
# x = rpalite.get_clipboard_text()
# rpalite.input_text(x)

# ps = rpalite.find_text_positions('OUTLINE')
# print(f"click by position: {ps[0]}")
# rpalite.click_by_position(ps[0][0], ps[0][1])

# not recommmand to use, unless there is no other way
# x = rpalite.find_control_near_text('Reset Password')
# rpalite.click_by_position(x[0], x[1])
# x = rpalite.find_control_by_label('Categories')
# rpalite.click_by_position(x[0], x[1])

# rpalite.send_keys('command+f')

#NOT test -----------------------------------------------------

# Test start_screen_recording function
# Note: This will start recording the screen
# recording_file = rpalite.start_screen_recording()
# print('Recording to:', recording_file)

# rpalite.sleep(5)
# Test stop_screen_recording function
# Note: This will stop the screen recording
# rpalite.stop_screen_recording()


# NOT Support ON MACOS
#rpalite.maximize_window(app)
#rpalite.close_app(app)
#app = rpalite.find_application(title='Untitled - Notepad')
# rpalite.find_control(app, class_name='Edit', title='Untitled - Notepad')
# rpalite.click_control(app, class_name='Edit', title='Untitled - Notepad')
# print(rpalite.locate('File'))