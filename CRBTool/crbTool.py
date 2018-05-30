"""This uses a Qt binding of "any" kind, thanks to the Qt.py module,
to produce an UI. First, one .ui file is loaded and then attaches
another .ui file onto the first. Think of it as creating a modular UI.

More on Qt.py:
https://github.com/mottosso/Qt.py
"""

import sys
import os
import fnmatch
import platform
from main import *

sys.dont_write_bytecode = True  # Avoid writing .pyc files

# ----------------------------------------------------------------------
# Environment detection
# ----------------------------------------------------------------------

try:
    import maya.cmds as cmds
    import pymel.core as pm
    import maya.mel as mel
    MAYA = True
except ImportError:
    MAYA = False

try:
    import nuke
    import nukescripts
    NUKE = True
except ImportError:
    NUKE = False

STANDALONE = False
if not MAYA and not NUKE:
    STANDALONE = True


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

# Window title and object names
WINDOW_TITLE = WINDOW_TITLE
WINDOW_OBJECT = WINDOW_OBJECT

# Maya-specific
DOCK_WITH_MAYA_UI = False

# Nuke-specific
DOCK_WITH_NUKE_UI = False

# Repository path
REPO_PATH = os.path.join(PATH, 'CRBTool')

# Palette filepath
PALETTE_FILEPATH = os.path.join(
    REPO_PATH, 'boilerdata', 'qpalette_maya2016.json')

# Full path to where .ui files are stored
UI_PATH = os.path.join(REPO_PATH, 'boilerdata')

# Qt.py option: Set up preffered binding
# os.environ['QT_PREFERRED_BINDING'] = 'PyQt4'
# os.environ['QT_PREFERRED_BINDING'] = 'PySide'
# os.environ['QT_PREFERRED_BINDING'] = 'PyQt5'
# os.environ['QT_PREFERRED_BINDING'] = 'PySide2'
if NUKE:
    # Avoid loading site-wide PyQt4/PyQt5 inside of Nuke
    os.environ['QT_PREFERRED_BINDING'] = 'PySide'


# ----------------------------------------------------------------------
# Set up Python modules access
# ----------------------------------------------------------------------

# Enable access to boilerlib (Qt.py, mayapalette)
if REPO_PATH not in sys.path:
    sys.path.append(REPO_PATH)

# ----------------------------------------------------------------------
# Main script
# ----------------------------------------------------------------------
import json

from boilerlib.Qt import QtWidgets  # pylint: disable=E0611
from boilerlib.Qt import QtCore  # pylint: disable=E0611
from boilerlib.Qt import QtCompat
from boilerlib.Qt import QtGui
from boilerlib.Qt.QtWidgets import QFileDialog

from boilerlib import mayapalette
from functools import partial
from collections import OrderedDict

# Debug
# print('Using' + QtCompat.__binding__)


class Boilerplate(QtWidgets.QMainWindow):
    """Example showing how UI files can be loaded using the same script
    when taking advantage of the Qt.py module and build-in methods
    from PySide/PySide2/PyQt4/PyQt5."""

    def __init__(self, parent=None):
        super(Boilerplate, self).__init__(parent)

        # Set object name and window title
        self.setObjectName(WINDOW_OBJECT)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QtGui.QIcon(os.path.join(UI_PATH, 'icons/win_icon.png')))
        # Window type
        self.setWindowFlags(QtCore.Qt.Window)

        if MAYA:
            # Makes Maya perform magic which makes the window stay
            # on top in OS X and Linux. As an added bonus, it'll
            # make Maya remember the window position
            self.setProperty("saveWindowPref", True)

        # Filepaths
        main_window_file = os.path.join(UI_PATH, MAIN_UI)
        # module_file = os.path.join(UI_PATH, 'module.ui')

        # Load UIs
        self.main_widget = QtCompat.load_ui(main_window_file)  # Main window UI
        self.object_action()

        self.event_show()

        # Set the main widget
        self.setCentralWidget(self.main_widget)

        self.setMaximumSize(1108, 692)


    def say_hello(self):
        print('Hello world!')
        # self.trig.emit()

    def object_action(self):
        from functools import partial
        
        self.act_ac = self.main_widget.actionActivate
        self.res_ac = self.main_widget.actionReset
        self.hel_ac = self.main_widget.actionHelp

        self.act_ac.triggered.connect(self.activate_ac)
        self.res_ac.triggered.connect(self.reset_ac)
        self.hel_ac.triggered.connect(self.help_ac)
        
        self.main_widget.action_pb.clicked.connect(self.run_action)
        self.main_widget.action_pb.setIcon(QtGui.QIcon(os.path.join(UI_PATH, 'icons/action.png')))

        # TODO: Tab Mini Script action
        self.main_widget.run_pb.clicked.connect(self.custom_run_action)

        self.act_cb = ( 
            self.main_widget.action_1_cb,
            self.main_widget.action_2_cb,
            self.main_widget.action_3_cb,
            self.main_widget.action_4_cb,
            self.main_widget.action_5_cb,
            self.main_widget.action_6_cb
        )

        self.la_pb = (
            self.main_widget.load_action_1_pb,
            self.main_widget.load_action_2_pb,
            self.main_widget.load_action_3_pb,
            self.main_widget.load_action_4_pb,
            self.main_widget.load_action_5_pb,
            self.main_widget.load_action_6_pb
        )

        self.cus_ac = (
            self.main_widget.cus_action_1_cb,
            self.main_widget.cus_action_2_cb,
            self.main_widget.cus_action_3_cb
        )

        self.ch_ac = (
            self.main_widget.check_action_1_cb,
            self.main_widget.check_action_2_cb,
            self.main_widget.check_action_3_cb
        )

        self.set_tooltip()

        for x in self.la_pb:
            self.check_icons(self.la_pb.index(x))
            x.clicked.connect(partial(self.load_pb, int(self.la_pb.index(x))))

        self.change_item(0)
        self.main_widget.sett_cb.activated.connect(self.change_item)
        
        for x in range(len(self.ch_ac)):
            self.cus_ac[x].setEnabled(False)
            self.ch_ac[x].stateChanged.connect(self.check_item)

        if os.path.isfile(CUS_FILE_PATH):
            self.set_item_list()
# ----------------------------------------------------------------------
# Tab Mini Action
# ----------------------------------------------------------------------    
    def custom_run_action(self):
        for x in range(len(self.ch_ac)):
            if self.ch_ac[x].isChecked() and self.main_widget.sett_cb.currentText() == 'Run Script':
                print('Run Script from {}:'.format(x))
                print('\t{}'.format(self.cus_ac[x].currentText()))
                self.run_item_list(x)

            elif self.ch_ac[x].isChecked() and self.main_widget.sett_cb.currentText() == 'Import Maya':
                print('Import Maya from {}'.format(x))
                self.run_item_list(x)

            elif self.ch_ac[x].isChecked() and self.main_widget.sett_cb.currentText() == 'Import Ref Maya':
                print('Import Ref Maya from {}'.format(x))
                self.run_item_list(x)
                
            elif self.ch_ac[x].isChecked() and self.main_widget.sett_cb.currentText() == 'Add Dir':
                print('Add item in {}'.format(x))

                get_folder = QFileDialog.getExistingDirectory(self, 'Get Directory Path {}'.format(x+1), 'C:/', QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

                if get_folder:
                    print(get_folder)
                    print('NO : {}'.format(x))
                    var_ = 'Directory ' + str(x+1)
                    path_ = get_folder.replace('\\', '/')
                    self.set_file(var_, path_)
                    self.set_item_list()

            elif self.ch_ac[x].isChecked() and self.main_widget.sett_cb.currentText() == 'Reset Dir':
                print('Reset Items {}'.format(x))
                self.set_file('boilerdata/cus_save.json', CUS_FILE_PATH)
                self.set_item_list()
            else:
                pass
    def run_item_list(self, x):
        with open(CUS_FILE_PATH, 'r') as load_file:
            load_json = json.load(load_file, object_pairs_hook=OrderedDict)
            load_key = load_json.keys()
            load_value = load_json.values()
        nam_file, typ_file = os.path.splitext(self.cus_ac[x].currentText())
        exec_file = os.path.join(load_value[x], self.cus_ac[x].currentText())

        print(exec_file)
        if load_value[x] != '':
            if self.main_widget.sett_cb.currentText() == 'Run Script':
                if typ_file == '.py':
                    print('RUN {}:'.format(load_value))
                    try:
                        exec(open(exec_file).read())
                        try:
                            print(show_print)
                            self.show_info('Information', show_print, QtGui.QMessageBox.Information)
                        except:
                            pass
                    except Exception as ex:
                        try:
                            self.show_info('Error', str(ex), QtGui.QMessageBox.Critical)
                        except:
                            print('ERROR: {}'.format(ex))
                #     print('RUN: {}'.format(load_value))
                #     try:
                #         exec(open(exec_file).read())
                #         main()
                #     except Exception as ex:
                #         print('ERROR: {}'.format(ex))
                # elif typ_file == '.mel':
                #     mel.eval(open(exec_file).read())
            elif self.main_widget.sett_cb.currentText() == 'Run Script':
                if typ_file == '.ma' or typ_file == '.mb':
                    print('\nCan not run {}, but must be imported!!\n'.format(exec_file))
                
            elif self.main_widget.sett_cb.currentText() == 'Import Ref Maya':
                if typ_file == '.ma':
                    pm.cmds.file("{}".format(exec_file), ignoreVersion=1, type="mayaAscii", namespace="{}".format(nam_file), r=1, gl=1, mergeNamespacesOnClash=False, options="v=0;p=17;f=0")
                elif typ_file == '.mb':
                    pm.cmds.file("{}".format(exec_file), ignoreVersion=1, type="mayaBinary", namespace="{}".format(nam_file), r=1, gl=1, mergeNamespacesOnClash=False, options="v=0;p=17;f=0")
            
            elif self.main_widget.sett_cb.currentText() == 'Import Maya':
                if typ_file == '.ma':
                    pm.cmds.file("{}".format(exec_file), pr=1, ignoreVersion=1, i=1, type="mayaAscii", namespace="{}".format(nam_file), ra=True, mergeNamespacesOnClash=False, options="v=0;p=17;f=0")
                elif typ_file == '.mb':
                    pm.cmds.file("{}".format(exec_file), pr=1, ignoreVersion=1, i=1, type="mayaBinary", namespace="{}".format(nam_file), ra=True, mergeNamespacesOnClash=False, options="v=0;p=17;f=0")

    # Set text pushbutton
    def change_item(self, pos):
        item_text = self.main_widget.run_pb.setText(self.main_widget.sett_cb.itemText(pos))
        if pos:
            item_text

    def check_item(self):
        for x in range(len(self.ch_ac)):
            if self.ch_ac[x].isChecked():
                self.cus_ac[x].setEnabled(True)
            else:
                self.cus_ac[x].setEnabled(False)

    def set_item_list(self):

        for x in range(len(self.cus_ac)):
            self.cus_ac[x].clear()
            with open(CUS_FILE_PATH, 'r') as load_file:
                load_json = json.load(load_file, object_pairs_hook=OrderedDict)
                load_key = load_json.keys()
                load_value = load_json.values()

            key_nam = 'Directory '+ str(x+1)
            if key_nam in load_key[x] and load_value[x] != '':
                for ldir in os.listdir(load_value[x]):
                    patterns = ['*.ma','*.py','*.mel','*.mb']
                    for patt in patterns:
                        if fnmatch.fnmatch(ldir, patt):
                            self.cus_ac[x].addItem(ldir)
                            
        print('\n== SET ITEMS LIST ==')
        
# ----------------------------------------------------------------------
# Tab Run Script
# ----------------------------------------------------------------------
    def run_action(self):
        for x in range(len(self.la_pb)):
            with open(FILE_PATH, 'r') as load_file:
                load_json = json.load(load_file, object_pairs_hook=OrderedDict)
                load_key = load_json.keys()[x]
                load_value = load_json.values()[x]
                if load_value != '' and self.act_cb[x].isChecked():
                    nam_file, typ_file = os.path.splitext(load_value)
                    if typ_file == '.py':
                        print('RUN {}:'.format(load_value))
                        try:
                            exec(open(load_value).read())
                            try:
                                print(show_print)
                                self.show_info('Information', show_print, QtGui.QMessageBox.Information)
                            except:
                                pass
                        except Exception as ex:
                            try:
                                self.show_info('Error', str(ex), QtGui.QMessageBox.Critical)
                            except:
                                print('ERROR: {}'.format(ex))

                    elif typ_file == '.mel':
                        print('RUN {}:'.format(load_value))
                        mel.eval(open(load_value).read())
                load_file.close()

        print('== CLEANING ==')

    def load_pb(self, pos):
        if self.act_cb[pos].isChecked():
            if 'Action {}'.format(pos+1) == self.act_cb[pos].text():
                print('ADD: {}'.format(self.act_cb[pos].text()))
            else:
                print('REPLACE: {}'.format(self.act_cb[pos].text()))
            self.open_dialog(pos)
            self.check_icons(pos)
        else:
            print('REMOVE: {}'.format(self.act_cb[pos].text()))

            load_file = open(os.path.join(REPO_PATH, 'boilerdata/save.json'), 'r')
            load_json = json.load(load_file)

            var = 'Action ' + str(pos+1)
            self.set_file(var, load_json.values()[pos])  
            print(load_json.values()[pos])          
            self.check_icons(pos)

            self.set_tooltip()

    def reset_ac(self):
        try:
            self.set_file('boilerdata/save.json', FILE_PATH)
            self.set_file('boilerdata/cus_save.json', CUS_FILE_PATH)
            self.set_item_list()
            for x in self.act_cb:
                x.setChecked(False)

            for x in self.la_pb:
                self.check_icons(self.la_pb.index(x))
            
            self.set_tooltip()

            print('== RESET ACTION ==')
        except:
            pass

    def help_ac(self):
        print('== HELP ACTION ==')

    def open_dialog(self, pos):
        file_name = QFileDialog.getOpenFileName(self, 'Get Path File', 'C:/', 'Script Files (*.mel *.py)')

        if file_name[0]:
            file_path = open(file_name[0], 'r')
            print('ADD ACTION:\n\tPOSITION: {}, PATH: {}'.format(pos+1,file_name[0]))
            var = 'Action ' + str(pos+1)
            # print(var)
            self.set_file(var, file_name[0])
            self.set_tooltip()

    def set_file(self, pos, path):
        PATH_ = path
        SAVE_PATH_ = pos
        # print(SAVE_PATH_, PATH_)
        if 'Action ' in pos:
            with open(FILE_PATH, 'r+') as load_file:
                load_json = json.load(load_file)
                load_json[pos] = str(path)
                load_file.seek(0)
                json.dump(load_json, load_file, sort_keys=True, indent=4)
                load_file.truncate()
                load_file.close()
        elif 'Directory ' in pos:
            with open(CUS_FILE_PATH, 'r+') as load_file:
                load_json = json.load(load_file)
                load_json[pos] = str(path)
                load_file.seek(0)
                json.dump(load_json, load_file, sort_keys=True, indent=4)
                load_file.truncate()
                load_file.close()
        else:
            create_file = open(PATH_, 'w')
            create_file.truncate()
            load_new_file = open(os.path.join(REPO_PATH, SAVE_PATH_), 'r')
            load_json = json.load(load_new_file)
            json.dump(load_json, create_file, sort_keys=True, indent=4)
            create_file.close()

    def set_tooltip(self):
        # pass
        if os.path.isfile(FILE_PATH):
            for x in range(len(self.act_cb)):
                with open(FILE_PATH, 'r') as load_file:
                    load_json = json.load(load_file, object_pairs_hook=OrderedDict)
                    load_value = load_json.values()[x]
                    if load_value != '':
                        nam_file, typ_file = os.path.splitext(load_value)
                        # nam = nam_file.split('/')[-1]
                        nam = nam_file + '.txt'
                        if os.path.isfile(nam):
                            tooltip_file = open(nam, 'r')
                            self.act_cb[x].setToolTip('{}'.format(tooltip_file.read()))
                        else:
                            self.act_cb[x].setToolTip('Directory: {}'.format(load_value))
                    else:
                        self.act_cb[x].setToolTip(None)
                    load_file.close()
# ----------------------------------------------------------------------
# Setting event show
# ----------------------------------------------------------------------
    def activate_ac(self):
        if not os.path.exists(DIR_PATH):
            os.makedirs(DIR_PATH)

            if not os.path.isfile(FILE_PATH):
                self.set_file('boilerdata/save.json', FILE_PATH)

            if not os.path.isfile(CUS_FILE_PATH):
                self.set_file('boilerdata/cus_save.json', CUS_FILE_PATH)
                self.set_item_list()

            self.event_show()
            print('== FOLDER & FILE CREATED ==')
        else:
            self.reset_ac()
            if os.path.isfile(FILE_PATH):
                os.remove(FILE_PATH)

            if os.path.isfile(CUS_FILE_PATH):
                os.remove(CUS_FILE_PATH)

            os.removedirs(DIR_PATH)
            for x in self.act_cb:
                x.setChecked(False)
            for x in self.la_pb:
                self.check_icons(self.la_pb.index(x))
            self.event_show()
            print('== FOLDER & FILE DELETED ==')

    def check_icons(self, pos):
        try:
            with open(FILE_PATH, 'r') as load_file:
                load_json = json.load(load_file, object_pairs_hook=OrderedDict)
                if len(load_json.values()[pos]) != 0:
                    self.la_pb[pos].setIcon(QtGui.QIcon(os.path.join(REPO_PATH, 'boilerdata/icons/minus.png')))
                    self.act_cb[pos].setText(self.set_nam(load_json.values()[pos]))
                else:
                    self.la_pb[pos].setIcon(QtGui.QIcon(os.path.join(REPO_PATH, 'boilerdata/icons/add.png')))
                    self.act_cb[pos].setText(self.set_nam(load_json.keys()[pos]))
        except:
            self.la_pb[pos].setIcon(QtGui.QIcon(os.path.join(REPO_PATH, 'boilerdata/icons/add.png')))
            pass         

    def event_show(self):
        if not os.path.exists(DIR_PATH):
            self.main_widget.tabWidget.setEnabled(False)
            self.res_ac.setEnabled(False)
            self.act_ac.setText('Activate')
        else:
            self.main_widget.tabWidget.setEnabled(True)
            self.res_ac.setEnabled(True)
            self.act_ac.setText('Deactivate')

    def set_nam(self, path):
        nam = str(os.path.basename(path))
        if '_' in nam:
            split_ = nam.split('.')[0].split('_')
            join_ = ' '.join(split_).title()
            return join_
        else:
            return nam

    def show_info(self, title, text, icon):
        info = QtGui.QMessageBox()
        info.setIcon(icon)
        info.setWindowTitle(title)
        info.setText(text)
        info.exec_()
        pass
# ----------------------------------------------------------------------
# DCC application helper functions
# ----------------------------------------------------------------------

def _maya_delete_ui():
    """Delete existing UI in Maya"""
    if cmds.window(WINDOW_OBJECT, q=True, exists=True):
        cmds.deleteUI(WINDOW_OBJECT)  # Delete window
    if cmds.dockControl('MayaWindow|' + WINDOW_TITLE, q=True, ex=True):
        cmds.deleteUI('MayaWindow|' + WINDOW_TITLE)  # Delete docked window


def _nuke_delete_ui():
    """Delete existing UI in Nuke"""
    for obj in QtWidgets.QApplication.allWidgets():
        if obj.objectName() == WINDOW_OBJECT:
            obj.deleteLater()


def _maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.qApp.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


def _nuke_main_window():
    """Returns Nuke's main window"""
    for obj in QtWidgets.qApp.topLevelWidgets():
        if (obj.inherits('QMainWindow') and
                obj.metaObject().className() == 'Foundry::UI::DockMainWindow'):
            return obj
    else:
        raise RuntimeError('Could not find DockMainWindow instance')


def _nuke_set_zero_margins(widget_object):
    """Remove Nuke margins when docked UI

    .. _More info:
        https://gist.github.com/maty974/4739917
    """
    parentApp = QtWidgets.QApplication.allWidgets()
    parentWidgetList = []
    for parent in parentApp:
        for child in parent.children():
            if widget_object.__class__.__name__ == child.__class__.__name__:
                parentWidgetList.append(
                    parent.parentWidget())
                parentWidgetList.append(
                    parent.parentWidget().parentWidget())
                parentWidgetList.append(
                    parent.parentWidget().parentWidget().parentWidget())

                for sub in parentWidgetList:
                    for tinychild in sub.children():
                        try:
                            tinychild.setContentsMargins(0, 0, 0, 0)
                        except:
                            pass


# ----------------------------------------------------------------------
# Run functions
# ----------------------------------------------------------------------

def run_maya():
    """Run in Maya"""
    _maya_delete_ui()  # Delete any existing existing UI
    crb = Boilerplate(parent=_maya_main_window())

    # Makes Maya perform magic which makes the window stay
    # on top in OS X and Linux. As an added bonus, it'll
    # make Maya remember the window position
    crb.setProperty("saveWindowPref", True)

    if not DOCK_WITH_MAYA_UI:
        crb.show()  # Show the UI
    elif DOCK_WITH_MAYA_UI:
        allowed_areas = ['right', 'left', 'bottom']
        cmds.dockControl(WINDOW_TITLE, label=WINDOW_TITLE, area='left',
                         content=WINDOW_OBJECT, allowedArea=allowed_areas)


def run_nuke():
    """Run in Nuke

    Note:
        If you want the UI to always stay on top, replace:
        `boil.ui.setWindowFlags(QtCore.Qt.Tool)`
        with:
        `boil.ui.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)`

        If you want the UI to be modal:
        `boil.ui.setWindowModality(QtCore.Qt.WindowModal)`
    """
    _nuke_delete_ui()  # Delete any alrady existing UI
    if not DOCK_WITH_NUKE_UI:
        boil = Boilerplate(parent=_nuke_main_window())
        boil.setWindowFlags(QtCore.Qt.Tool)
        boil.show()  # Show the UI
    elif DOCK_WITH_NUKE_UI:
        prefix = ''
        basename = os.path.basename(__file__)
        module_name = basename[: basename.rfind('.')]
        if __name__ == module_name:
            prefix = module_name + '.'
        panel = nukescripts.panels.registerWidgetAsPanel(
            widget=prefix + 'Boilerplate',  # module_name.Class_name
            name=WINDOW_TITLE,
            id='uk.co.thefoundry.' + WINDOW_TITLE,
            create=True)
        pane = nuke.getPaneFor('Properties.1')
        panel.addToPane(pane)
        boil = panel.customKnob.getObject().widget
        _nuke_set_zero_margins(boil)


def run_standalone():
    """Run standalone

    Note:
        Styling the UI with the Maya palette on OS X when using the
        PySide/PyQt4 bindings result in various issues, which is why
        it is disabled by default when you're running this combo.

    .. _Issue #9:
       https://github.com/fredrikaverpil/pyvfx-boilerplate/issues/9
    """
    app = QtWidgets.QApplication(sys.argv)
    boil = Boilerplate()
    if not (platform.system() == 'Darwin' and
            (QtCompat.__binding__ == 'PySide' or QtCompat.__binding__ == 'PyQt4')):
        mayapalette.set_maya_palette_with_tweaks(PALETTE_FILEPATH)
    boil.show()  # Show the UI
    sys.exit(app.exec_())


if __name__ == "__main__":
    if MAYA:
        run_maya()
    elif NUKE:
        run_nuke()
    else:
        run_standalone()
