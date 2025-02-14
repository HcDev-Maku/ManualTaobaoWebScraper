from selenium import webdriver
import pygetwindow as gw

import time, os, json

script = """
(function() {
    let button = document.createElement("button");
    button.innerText = "GetDetails";
    button.style.position = "fixed";
    button.style.bottom = "20px";
    button.style.right = "20px";
    button.style.padding = "10px 20px";
    button.style.background = "#007BFF";
    button.style.color = "white";
    button.style.border = "none";
    button.style.borderRadius = "5px";
    button.style.cursor = "pointer";
    button.style.zIndex = "9999";

    button.onclick = function() {
        let div = document.createElement('div');
        div.innerHTML = '<div style="position:fixed;top:50%;left:50%;transform:translate(-50%, -50%);padding:20px;background:white;border:2px solid black;z-index:10000; font-size: 20px;"> Hecker, Maku Santiran was here <br><br> <center> <button style="font-size:15px; padding:5px;" onclick="this.parentElement.parentElement.remove()">Close</button> </center> </div>';
        document.body.appendChild(div);
        //alert("Hecker Detected Maku Santiran!");
    };

    document.body.appendChild(button);
})();
"""

# Selenium, why
def getPreviousProfile(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        #end
        # Look for the "last_used" field inside the "profile" dictionary.
        last_used_profile = local_state.get("profile", {}).get("last_used", "Default")
        return last_used_profile
    except Exception as e:
        print("Error reading last used profile:", e)
        return "Default"
    #end
#end

user_home = os.path.expanduser("~")
local_state_path = os.path.join(user_home, "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
default_profile_path = os.path.join(user_home, "AppData", "Local", "Google", "Chrome", "User Data")
profile_directory = getPreviousProfile(local_state_path)

print(f"Going to use {profile_directory}")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument(f"--user-data-dir={default_profile_path}")
chrome_options.add_argument(f"--profile-directory={profile_directory}")

if __name__ == '__main__':
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://taobao.com")
    previous_url = driver.current_url  # Store the initial URL
    previous_tab = driver.current_window_handle
    driver.execute_script(script)

    #driver.execute_script("""
    #    document.querySelectorAll("a[target='_blank']").forEach(el => el.target = "_self");
    #""")

    # Track initial tabs
    previous_tabs = set(driver.window_handles)
    tab_map = {}  # Dictionary to store {title: handle}tab_map = {}  # Dictionary to store {title: handle}

    while True:
        current_tabs = set(driver.window_handles)
        current_url = driver.current_url

        indexed_title = f'{driver.title}_{driver.window_handles.index(driver.current_window_handle)}'
        tab_map[driver.title] = driver.current_window_handle
        driver.execute_script(script)
        
        # Detect new tabs
        for handle in current_tabs:
            if handle not in tab_map.values():  # New tab detected
                driver.switch_to.window(handle)
                #driver.execute_script(f"document.title = '{indexed_title}';")
                print(f"New tab detected: {driver.title}")
                tab_map[driver.title] = handle  # Store it in dictionary
            #end
        #end

        # Detect closed tabs
        closed_tabs = set(tab_map.values()) - current_tabs
        for handle in closed_tabs:
            title_to_remove = [title for title, h in tab_map.items() if h == handle]
            if title_to_remove:
                del tab_map[title_to_remove[0]]
                print(f"Tab closed: {title_to_remove[0]}")
            #end
        #end
        
        # Detect active tab (without switching focus)
        active_tab = driver.current_window_handle
        print(f"User is currently on tab: {driver.window_handles.index(driver.current_window_handle)}, length of tabs: {len(driver.window_handles)}")

        # Update previous state
        previous_tabs = current_tabs

        active_window = gw.getActiveWindow()
        if active_window and "Chrome" in active_window.title:
            active_title = active_window.title.replace(" - Google Chrome", "").strip()
            try:
                driver.switch_to.window(tab_map[active_title])
            except:
                print("a")
            #end
            print(active_title, tab_map)
        #end

        time.sleep(0.5)  # Adjust polling rate
    #end
#end