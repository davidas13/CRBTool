import sys, os

sys.dont_write_bytecode = True 
# ----------------------------------------------------------------------
# Path setup
# ----------------------------------------------------------------------
STRING_PATH = 'G:/temp/David/crbTool'
PATH = os.path.normpath(STRING_PATH)
print(PATH)
WINDOW_TITLE = 'CRB Tool'
WINDOW_OBJECT = 'crb_tool'

MAIN_UI = 'crb_window.ui'

DIR_PATH = 'C:/CRBTool'

FILE_PATH = os.path.join(DIR_PATH, 'save.json')
CUS_FILE_PATH = os.path.join(DIR_PATH, 'cus_save.json')

# ICON_PATH = ''

# BUTTON_ICON_PATH = ''



# ----------------------------------------------------------------------
# Main script
# ----------------------------------------------------------------------
def main():
    if PATH not in sys.path:
        sys.path.append(PATH)
    
    import CRBTool.crbTool as crb
    reload(crb)
    crb.run_maya()


if __name__=='__main__':
    main()
