"""----------------------------------------------------------------------------
   jogging.py

   Copyright (C) 2013-2017 Wilhelm Duembeg

   This file is part of gsat. gsat is a cross-platform GCODE debug/step for
   Grbl like GCODE interpreters. With features similar to software debuggers.
   Features such as breakpoint, change current program counter, inspection
   and modification of variables.

   gsat is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 2 of the License, or
   (at your option) any later version.

   gsat is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with gsat.  If not, see <http://www.gnu.org/licenses/>.

----------------------------------------------------------------------------"""

import os
import re
import wx
from wx.lib import scrolledpanel as scrolled
from wx.lib.agw import floatspin as fs

import modules.config as gc
import modules.machif_config as mi


"""----------------------------------------------------------------------------
   gsatJoggingSettingsPanel:
   Machine settings.
----------------------------------------------------------------------------"""
class gsatJoggingSettingsPanel(scrolled.ScrolledPanel):
   def __init__(self, parent, config_data, **args):
      scrolled.ScrolledPanel.__init__(self, parent,
         style=wx.TAB_TRAVERSAL|wx.NO_BORDER)

      self.configData = config_data

      self.InitUI()
      self.SetAutoLayout(True)
      self.SetupScrolling()
      #self.FitInside()

   def InitUI(self):
      vBoxSizer = wx.BoxSizer(wx.VERTICAL)

      text = wx.StaticText(self, label="General")
      font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
      text.SetFont(font)
      vBoxSizer.Add(text, 0, wx.ALL, border=5)

      # Add readonly check box
      self.cbXYZReadOnly = wx.CheckBox(self, wx.ID_ANY, "XYZ Read Only Status")
      self.cbXYZReadOnly.SetValue(self.configData.Get('/jogging/XYZReadOnly'))
      self.cbXYZReadOnly.SetToolTip(
         wx.ToolTip("If enabled the XYZ fields in jogging status become read only"))
      vBoxSizer.Add(self.cbXYZReadOnly, flag=wx.LEFT, border=20)

      # Add update from machine pos check box
      self.cbAutoMPOS = wx.CheckBox(self, wx.ID_ANY, "Auto update from machine position")
      self.cbAutoMPOS.SetValue(self.configData.Get('/jogging/AutoMPOS'))
      self.cbAutoMPOS.SetToolTip(
         wx.ToolTip("Use Machine position to auto update Jogging position, "\
            "jogging operation use these values to operate. The JOG current "
            "position need to be in sync with machine position before "\
            "starting any jog operation. Results maybe undesirable otherwise"))
      vBoxSizer.Add(self.cbAutoMPOS, flag=wx.LEFT, border=20)

      # Add request status after jogging set operation check box
      self.cbReqUpdateOnJogSetOp = wx.CheckBox(self, wx.ID_ANY, "Request update after JOG set operation")
      self.cbReqUpdateOnJogSetOp.SetValue(self.configData.Get('/jogging/ReqUpdateOnJogSetOp'))
      self.cbReqUpdateOnJogSetOp.SetToolTip(
         wx.ToolTip("If enable after each JOG set operation (ie set to ZERO) a machine update request will be sent to device"))
      vBoxSizer.Add(self.cbReqUpdateOnJogSetOp, flag=wx.LEFT|wx.BOTTOM, border=20)

      # Custom controls
      text = wx.StaticText(self, label="Custom Controls")
      font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
      text.SetFont(font)
      vBoxSizer.Add(text, 0, wx.ALL, border=5)

      box1, c1CtrlArray = self.CreateCustomControlSettings(1)
      box2, c2CtrlArray = self.CreateCustomControlSettings(2)
      box3, c3CtrlArray = self.CreateCustomControlSettings(3)
      box4, c4CtrlArray = self.CreateCustomControlSettings(4)

      self.customCtrlArray = [c1CtrlArray, c2CtrlArray, c3CtrlArray, c4CtrlArray]

      vBoxSizer.Add(box1, 0, flag=wx.LEFT|wx.EXPAND, border=20)
      vBoxSizer.Add(box2, 0, flag=wx.LEFT|wx.EXPAND, border=20)
      vBoxSizer.Add(box3, 0, flag=wx.LEFT|wx.EXPAND, border=20)
      vBoxSizer.Add(box4, 0, flag=wx.LEFT|wx.EXPAND, border=20)

      self.SetSizer(vBoxSizer)

   def CreateCustomControlSettings(self, cn):
      # Custom controls
      vBoxSizerRoot = wx.BoxSizer(wx.VERTICAL)
      text = wx.StaticText(self, label="Custom Control %d" % cn)
      font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
      text.SetFont(font)
      vBoxSizerRoot.Add(text, 0, flag=wx.ALL, border=5)

      # Label
      hBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
      text = wx.StaticText(self, label="Label")
      hBoxSizer.Add(text, 0, flag=wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.RIGHT|wx.BOTTOM, border=5)
      tcLabel = wx.TextCtrl(self, -1,
         self.configData.Get('/jogging/Custom%dLabel' % cn), size=(125, -1))
      hBoxSizer.Add(tcLabel, 0, flag=wx.ALIGN_CENTER_VERTICAL)

      # radio buttons (position/script)
      positionRadioButton = wx.RadioButton(self, -1, 'Position', style=wx.RB_GROUP)
      positionRadioButton.SetValue(self.configData.Get('/jogging/Custom%dOptPosition' % cn))
      hBoxSizer.Add(positionRadioButton, flag=wx.LEFT|wx.EXPAND, border=5)

      scriptRadioButton = wx.RadioButton(self, -1, 'Script')
      scriptRadioButton.SetValue(self.configData.Get('/jogging/Custom%dOptScript' % cn))
      hBoxSizer.Add(scriptRadioButton, flag=wx.LEFT|wx.EXPAND, border=5)

      vBoxSizerRoot.Add(hBoxSizer, 0, flag=wx.LEFT|wx.EXPAND, border=20)

      # position controls
      vBoxSizer = wx.BoxSizer(wx.VERTICAL)
      text = wx.StaticText(self, label="Position")
      vBoxSizer.Add(text, 0, flag=wx.ALIGN_CENTER_VERTICAL|wx.TOP, border=5)

      gCustomSizer = wx.FlexGridSizer(3,3,0,0)

      text = wx.StaticText(self, label="X Settings")
      gCustomSizer.Add(text, flag=wx.LEFT|wx.ALIGN_BOTTOM, border=5)
      text = wx.StaticText(self, label="Y Settings")
      gCustomSizer.Add(text, flag=wx.LEFT|wx.ALIGN_BOTTOM, border=5)
      text = wx.StaticText(self, label="Z Settings")
      gCustomSizer.Add(text, flag=wx.LEFT|wx.ALIGN_BOTTOM, border=5)

      # check boxes
      cbXIsOffset = wx.CheckBox(self, wx.ID_ANY, "Is Offset")
      cbXIsOffset.SetValue(self.configData.Get('/jogging/Custom%dXIsOffset' % cn))
      cbXIsOffset.SetToolTip(wx.ToolTip("If set the value is treated as an offset"))
      gCustomSizer.Add(cbXIsOffset, flag=wx.ALL, border=5)

      cbYIsOffset = wx.CheckBox(self, wx.ID_ANY, "Is Offset")
      cbYIsOffset.SetValue(self.configData.Get('/jogging/Custom%dYIsOffset' % cn))
      cbYIsOffset.SetToolTip(wx.ToolTip("If set the value is treated as an offset"))
      gCustomSizer.Add(cbYIsOffset, flag=wx.ALL, border=5)

      cbZIsOffset = wx.CheckBox(self, wx.ID_ANY, "Is Offset")
      cbZIsOffset.SetValue(self.configData.Get('/jogging/Custom%dZIsOffset' % cn))
      cbZIsOffset.SetToolTip(wx.ToolTip("When set the value is treated as an offset"))
      gCustomSizer.Add(cbZIsOffset, flag=wx.ALL, border=5)

      # spin controls
      scXValue = fs.FloatSpin(self, -1,
         min_val=-100000, max_val=100000, increment=0.10, value=1.0,
         agwStyle=fs.FS_LEFT)
      scXValue.SetFormat("%f")
      scXValue.SetDigits(4)
      scXValue.SetValue(self.configData.Get('/jogging/Custom%dXValue' % cn))
      gCustomSizer.Add(scXValue, flag=wx.ALL, border=5)

      scYValue = fs.FloatSpin(self, -1,
         min_val=-100000, max_val=100000, increment=0.10, value=1.0,
         agwStyle=fs.FS_LEFT)
      scYValue.SetFormat("%f")
      scYValue.SetDigits(4)
      scYValue.SetValue(self.configData.Get('/jogging/Custom%dYValue' % cn))
      gCustomSizer.Add(scYValue,
         flag=wx.ALL|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)

      scZValue = fs.FloatSpin(self, -1,
         min_val=-100000, max_val=100000, increment=0.10, value=1.0,
         agwStyle=fs.FS_LEFT)
      scZValue.SetFormat("%f")
      scZValue.SetDigits(4)
      scZValue.SetValue(self.configData.Get('/jogging/Custom%dZValue' % cn))
      gCustomSizer.Add(scZValue,
         flag=wx.ALL|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)

      vBoxSizer.Add(gCustomSizer, 0, flag=wx.LEFT|wx.EXPAND, border=5)
      vBoxSizerRoot.Add(vBoxSizer, 0, flag=wx.LEFT|wx.EXPAND, border=20)

      # add edit control for script
      vBoxSizer = wx.BoxSizer(wx.VERTICAL)

      text = wx.StaticText(self, wx.ID_ANY, "Script")
      vBoxSizer.Add(text, 0, flag=wx.ALIGN_CENTER_VERTICAL)

      tcScript = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE)
      tcScript.SetValue(self.configData.Get('/jogging/Custom%dScript' % cn))
      #tcScript.SetToolTip(wx.ToolTip("This script is sent to device upon connect detect"))
      vBoxSizer.Add(tcScript, 1, flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.LEFT, border=10)

      vBoxSizerRoot.Add(vBoxSizer, 1, flag=wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, border=20)

      return vBoxSizerRoot, [
         tcLabel, positionRadioButton, scriptRadioButton,
         cbXIsOffset, cbYIsOffset, cbZIsOffset,
         scXValue   , scYValue   , scZValue,
         tcScript
      ]

   def UpdatConfigData(self):
      self.configData.Set('/jogging/XYZReadOnly', self.cbXYZReadOnly.GetValue())
      self.configData.Set('/jogging/AutoMPOS', self.cbAutoMPOS.GetValue())
      self.configData.Set('/jogging/ReqUpdateOnJogSetOp', self.cbReqUpdateOnJogSetOp.GetValue())

      for cn in range(4):
         cnp1 = cn+1
         self.configData.Set('/jogging/Custom%dLabel' % cnp1,
            self.customCtrlArray[cn][0].GetValue())

         self.configData.Set('/jogging/Custom%dOptPosition' % cnp1,
            self.customCtrlArray[cn][1].GetValue())
         self.configData.Set('/jogging/Custom%dOptScript' % cnp1,
            self.customCtrlArray[cn][2].GetValue())

         self.configData.Set('/jogging/Custom%dXIsOffset' % cnp1,
            self.customCtrlArray[cn][3].GetValue())
         self.configData.Set('/jogging/Custom%dYIsOffset' % cnp1,
            self.customCtrlArray[cn][4].GetValue())
         self.configData.Set('/jogging/Custom%dZIsOffset' % cnp1,
            self.customCtrlArray[cn][5].GetValue())

         self.configData.Set('/jogging/Custom%dXValue' % cnp1,
            self.customCtrlArray[cn][6].GetValue())
         self.configData.Set('/jogging/Custom%dYValue' % cnp1,
            self.customCtrlArray[cn][7].GetValue())
         self.configData.Set('/jogging/Custom%dZValue' % cnp1,
            self.customCtrlArray[cn][8].GetValue())
         self.configData.Set('/jogging/Custom%dScript' % cnp1,
            self.customCtrlArray[cn][9].GetValue())

"""----------------------------------------------------------------------------
   gsatCliSettingsPanel:
   CLI settings.
----------------------------------------------------------------------------"""
class gsatCliSettingsPanel(scrolled.ScrolledPanel):
   def __init__(self, parent, config_data, **args):
      scrolled.ScrolledPanel.__init__(self, parent,
         style=wx.TAB_TRAVERSAL|wx.NO_BORDER)

      self.configData = config_data

      self.InitUI()
      self.SetAutoLayout(True)
      self.SetupScrolling()
      #self.FitInside()

   def InitUI(self):
      vBoxSizer = wx.BoxSizer(wx.VERTICAL)

      # Add cehck box
      hBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
      self.cb = wx.CheckBox(self, wx.ID_ANY, "Save Command History")
      self.cb.SetValue(self.configData.Get('/cli/SaveCmdHistory'))
      hBoxSizer.Add(self.cb, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
      vBoxSizer.Add(hBoxSizer, flag=wx.TOP|wx.LEFT, border=20)

      # Add spin ctrl
      hBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
      self.sc = wx.SpinCtrl(self, wx.ID_ANY, "")
      self.sc.SetRange(1,1000)
      self.sc.SetValue(self.configData.Get('/cli/CmdMaxHistory'))
      hBoxSizer.Add(self.sc, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

      st = wx.StaticText(self, wx.ID_ANY, "Max Command History")
      hBoxSizer.Add(st, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

      vBoxSizer.Add(hBoxSizer, 0, flag=wx.LEFT|wx.EXPAND, border=20)
      self.SetSizer(vBoxSizer)

   def UpdatConfigData(self):
      self.configData.Set('/cli/SaveCmdHistory', self.cb.GetValue())
      self.configData.Set('/cli/CmdMaxHistory', self.sc.GetValue())

"""----------------------------------------------------------------------------
   gsatJoggingPanel:
   Jog controls for the machine as well as custom user controls.
----------------------------------------------------------------------------"""
class gsatJoggingPanel(wx.ScrolledWindow):
   def __init__(self, parent, config_data, state_data, **args):
      wx.ScrolledWindow.__init__(self, parent, **args)

      self.mainWindow = parent

      self.configData = config_data
      self.stateData = state_data

      self.memoX = gc.gZeroString
      self.memoY = gc.gZeroString
      self.memoZ = gc.gZeroString

      self.cliCommand = ""
      self.cliIndex = 0

      self.InitConfig()
      self.InitUI()
      width,height = self.GetSizeTuple()
      scroll_unit = 10
      self.SetScrollbars(scroll_unit,scroll_unit, width/scroll_unit, height/scroll_unit)

      self.UpdateSettings(self.configData)
      #self.allCheckBox.SetValue(True)
      #self.spinCtrl.SetFocus()
      self.LoadCli()

   def InitConfig(self):
      # jogging data
      self.configXYZReadOnly         = self.configData.Get('/jogging/XYZReadOnly')
      self.configAutoMPOS            = self.configData.Get('/jogging/AutoMPOS')
      self.configReqUpdateOnJogSetOp = self.configData.Get('/jogging/ReqUpdateOnJogSetOp')

      self.configCustom1Label       = self.configData.Get('/jogging/Custom1Label')
      self.configCustom1OptPosition = self.configData.Get('/jogging/Custom1OptPosition')
      self.configCustom1OptScript   = self.configData.Get('/jogging/Custom1OptScript')
      self.configCustom1XIsOffset   = self.configData.Get('/jogging/Custom1XIsOffset')
      self.configCustom1XValue      = self.configData.Get('/jogging/Custom1XValue')
      self.configCustom1YIsOffset   = self.configData.Get('/jogging/Custom1YIsOffset')
      self.configCustom1YValue      = self.configData.Get('/jogging/Custom1YValue')
      self.configCustom1ZIsOffset   = self.configData.Get('/jogging/Custom1ZIsOffset')
      self.configCustom1ZValue      = self.configData.Get('/jogging/Custom1ZValue')
      self.configCustom1Script      = self.configData.Get('/jogging/Custom1Script')

      self.configCustom2Label       = self.configData.Get('/jogging/Custom2Label')
      self.configCustom2OptPosition = self.configData.Get('/jogging/Custom2OptPosition')
      self.configCustom2OptScript   = self.configData.Get('/jogging/Custom2OptScript')
      self.configCustom2XIsOffset   = self.configData.Get('/jogging/Custom2XIsOffset')
      self.configCustom2XValue      = self.configData.Get('/jogging/Custom2XValue')
      self.configCustom2YIsOffset   = self.configData.Get('/jogging/Custom2YIsOffset')
      self.configCustom2YValue      = self.configData.Get('/jogging/Custom2YValue')
      self.configCustom2ZIsOffset   = self.configData.Get('/jogging/Custom2ZIsOffset')
      self.configCustom2ZValue      = self.configData.Get('/jogging/Custom2ZValue')
      self.configCustom2Script      = self.configData.Get('/jogging/Custom2Script')

      self.configCustom3Label       = self.configData.Get('/jogging/Custom3Label')
      self.configCustom3OptPosition = self.configData.Get('/jogging/Custom3OptPosition')
      self.configCustom3OptScript   = self.configData.Get('/jogging/Custom3OptScript')
      self.configCustom3XIsOffset   = self.configData.Get('/jogging/Custom3XIsOffset')
      self.configCustom3XValue      = self.configData.Get('/jogging/Custom3XValue')
      self.configCustom3YIsOffset   = self.configData.Get('/jogging/Custom3YIsOffset')
      self.configCustom3YValue      = self.configData.Get('/jogging/Custom3YValue')
      self.configCustom3ZIsOffset   = self.configData.Get('/jogging/Custom3ZIsOffset')
      self.configCustom3ZValue      = self.configData.Get('/jogging/Custom3ZValue')
      self.configCustom3Script      = self.configData.Get('/jogging/Custom3Script')

      self.configCustom4Label       = self.configData.Get('/jogging/Custom4Label')
      self.configCustom4OptPosition = self.configData.Get('/jogging/Custom4OptPosition')
      self.configCustom4OptScript   = self.configData.Get('/jogging/Custom4OptScript')
      self.configCustom4XIsOffset   = self.configData.Get('/jogging/Custom4XIsOffset')
      self.configCustom4XValue      = self.configData.Get('/jogging/Custom4XValue')
      self.configCustom4YIsOffset   = self.configData.Get('/jogging/Custom4YIsOffset')
      self.configCustom4YValue      = self.configData.Get('/jogging/Custom4YValue')
      self.configCustom4ZIsOffset   = self.configData.Get('/jogging/Custom4ZIsOffset')
      self.configCustom4ZValue      = self.configData.Get('/jogging/Custom4ZValue')
      self.configCustom4Script      = self.configData.Get('/jogging/Custom4Script')

      # cli data
      self.cliSaveCmdHistory      = self.configData.Get('/cli/SaveCmdHistory')
      self.cliCmdMaxHistory       = self.configData.Get('/cli/CmdMaxHistory')
      self.cliCmdHistory          = self.configData.Get('/cli/CmdHistory')


   def UpdateSettings(self, config_data):
      self.configData = config_data
      self.InitConfig()

      if self.configXYZReadOnly:
         self.jX.SetEditable(False)
         self.jX.SetBackgroundColour(gc.gReadOnlyBkColor)
         self.jY.SetEditable(False)
         self.jY.SetBackgroundColour(gc.gReadOnlyBkColor)
         self.jZ.SetEditable(False)
         self.jZ.SetBackgroundColour(gc.gReadOnlyBkColor)
      else:
         self.jX.SetEditable(True)
         self.jX.SetBackgroundColour(gc.gEdityBkColor)
         self.jY.SetEditable(True)
         self.jY.SetBackgroundColour(gc.gEdityBkColor)
         self.jZ.SetEditable(True)
         self.jZ.SetBackgroundColour(gc.gEdityBkColor)

      self.useWorkPosCheckBox.SetValue(self.configAutoMPOS)

      self.custom1Button.SetLabel(self.configCustom1Label)
      self.custom2Button.SetLabel(self.configCustom2Label)
      self.custom3Button.SetLabel(self.configCustom3Label)
      self.custom4Button.SetLabel(self.configCustom4Label)

   def InitUI(self):
      vPanelBoxSizer = wx.BoxSizer(wx.VERTICAL)
      hPanelBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

      # Add CLI
      self.cliComboBox = wx.combo.BitmapComboBox(self, style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER|wx.WANTS_CHARS)
      self.cliComboBox.SetToolTip(wx.ToolTip("Command Line Interface (CLI)"))
      self.cliComboBox.Bind(wx.EVT_TEXT_ENTER, self.OnCliEnter)
      #self.cliComboBox.Bind(wx.EVT_CHAR, self.OnCliChar)
      self.cliComboBox.Bind(wx.EVT_KEY_DOWN, self.OnCliKeyDown)
      #self.cliComboBox.Bind(wx.EVT_KEY_UP, self.OnCliKeyUp)
      vPanelBoxSizer.Add(self.cliComboBox, 0, wx.EXPAND|wx.ALL, border=1)


      # Add Controls ----------------------------------------------------------
      joggingControls = self.CreateJoggingControls()
      vPanelBoxSizer.Add(joggingControls, 0, flag=wx.ALL|wx.EXPAND, border=5)

      positionStatusControls = self.CreatePositionStatusControls()
      hPanelBoxSizer.Add(positionStatusControls, 0, flag=wx.EXPAND)

      gotoResetControls = self.CreateGotoAndResetControls()
      hPanelBoxSizer.Add(gotoResetControls, 0, flag=wx.LEFT|wx.EXPAND, border=10)

      vPanelBoxSizer.Add(hPanelBoxSizer, 0, flag=wx.ALL|wx.EXPAND, border=5)

      utilControls = self.CreateUtilControls()
      vPanelBoxSizer.Add(utilControls, 0, flag=wx.ALL|wx.EXPAND, border=5)


      # Finish up init UI
      self.SetSizer(vPanelBoxSizer)
      self.Layout()

   def UpdateUI(self, stateData, statusData=None):
      self.stateData = stateData

      if statusData is not None and self.configAutoMPOS:
         x = statusData.get('posx')
         if x is not None:
            self.jX.SetValue("{:.3f}".format(x))

         y = statusData.get('posy')
         if y is not None:
            self.jY.SetValue("{:.3f}".format(y))

         z = statusData.get('posz')
         if z is not None:
            self.jZ.SetValue("{:.3f}".format(z))

      if stateData.serialPortIsOpen and not stateData.swState == gc.gSTATE_RUN:
         self.resetToZeroButton.Enable()
         self.resetToJogButton.Enable()
         self.gotoToZeroButton.Enable()
         self.gotoToJogButton.Enable()
         self.gotoToHomeButton.Enable()
         self.positiveXButton.Enable()
         self.negativeXButton.Enable()
         self.positiveYButton.Enable()
         self.negativeYButton.Enable()
         self.positiveZButton.Enable()
         self.negativeZButton.Enable()
         self.spindleOnButton.Enable()
         self.spindleOffButton.Enable()
         self.custom1Button.Enable()
         self.custom2Button.Enable()
         self.custom3Button.Enable()
         self.custom4Button.Enable()
         self.cliComboBox.Enable()
      else:
         self.resetToZeroButton.Disable()
         self.resetToJogButton.Disable()
         self.gotoToZeroButton.Disable()
         self.gotoToJogButton.Disable()
         self.gotoToHomeButton.Disable()
         self.positiveXButton.Disable()
         self.negativeXButton.Disable()
         self.positiveYButton.Disable()
         self.negativeYButton.Disable()
         self.positiveZButton.Disable()
         self.negativeZButton.Disable()
         self.spindleOnButton.Disable()
         self.spindleOffButton.Disable()
         self.custom1Button.Disable()
         self.custom2Button.Disable()
         self.custom3Button.Disable()
         self.custom4Button.Disable()
         self.cliComboBox.Disable()


   def CreateJoggingControls(self):
      # Add Buttons -----------------------------------------------------------
      hButtonBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
      vYButtonBoxSizer = wx.BoxSizer(wx.VERTICAL)
      vZButtonBoxSizer = wx.BoxSizer(wx.VERTICAL)
      vOtherButtonBoxSizer = wx.BoxSizer(wx.VERTICAL)

      buttonSize = (50,50)

      self.negativeXButton = wx.Button(self, label="-X", size=buttonSize)
      self.negativeXButton.SetToolTip(
         wx.ToolTip("Move X axis on negative direction by step size"))
      self.Bind(wx.EVT_BUTTON, self.OnXNeg, self.negativeXButton)
      hButtonBoxSizer.Add(self.negativeXButton, flag=wx.ALIGN_CENTER_VERTICAL)

      self.positiveYButton = wx.Button(self, label="+Y", size=buttonSize)
      self.positiveYButton.SetToolTip(
         wx.ToolTip("Move Y axis on positive direction by step size"))
      self.Bind(wx.EVT_BUTTON, self.OnYPos, self.positiveYButton)
      vYButtonBoxSizer.Add(self.positiveYButton)

      self.negativeYButton = wx.Button(self, label="-Y", size=buttonSize)
      self.negativeYButton.SetToolTip(
         wx.ToolTip("Move Y axis on negative direction by step size"))
      self.Bind(wx.EVT_BUTTON, self.OnYNeg, self.negativeYButton)
      vYButtonBoxSizer.Add(self.negativeYButton)
      hButtonBoxSizer.Add(vYButtonBoxSizer, flag=wx.ALIGN_CENTER_VERTICAL)

      self.positiveXButton = wx.Button(self, label="+X", size=buttonSize)
      self.positiveXButton.SetToolTip(
         wx.ToolTip("Move X axis on positive direction by step size"))
      self.Bind(wx.EVT_BUTTON, self.OnXPos, self.positiveXButton)
      hButtonBoxSizer.Add(self.positiveXButton, flag=wx.ALIGN_CENTER_VERTICAL)

      spacerText = wx.StaticText(self, label="   ")
      hButtonBoxSizer.Add(spacerText, flag=wx.ALIGN_CENTER_VERTICAL)

      self.positiveZButton = wx.Button(self, label="+Z", size=buttonSize)
      self.positiveZButton.SetToolTip(
         wx.ToolTip("Move Z axis on positive direction by step size"))
      self.Bind(wx.EVT_BUTTON, self.OnZPos, self.positiveZButton)
      vZButtonBoxSizer.Add(self.positiveZButton)

      self.negativeZButton = wx.Button(self, label="-Z", size=buttonSize)
      self.negativeZButton.SetToolTip(
         wx.ToolTip("Move Z axis on negative direction by step size"))
      self.Bind(wx.EVT_BUTTON, self.OnZNeg, self.negativeZButton)
      vZButtonBoxSizer.Add(self.negativeZButton)
      hButtonBoxSizer.Add(vZButtonBoxSizer, flag=wx.ALIGN_CENTER_VERTICAL)

      spacerText = wx.StaticText(self, label="     ")
      hButtonBoxSizer.Add(spacerText, flag=wx.ALIGN_CENTER_VERTICAL)

      self.spindleOnButton = wx.Button(self, label="SP ON", size=(60,50))
      self.spindleOnButton.SetToolTip(wx.ToolTip("Spindle ON"))
      self.Bind(wx.EVT_BUTTON, self.OnSpindleOn, self.spindleOnButton)
      vOtherButtonBoxSizer.Add(self.spindleOnButton)

      self.spindleOffButton = wx.Button(self, label="SP OFF", size=(60,50))
      self.spindleOffButton.SetToolTip(wx.ToolTip("Spindle OFF"))
      self.Bind(wx.EVT_BUTTON, self.OnSpindleOff, self.spindleOffButton)
      vOtherButtonBoxSizer.Add(self.spindleOffButton)

      hButtonBoxSizer.Add(vOtherButtonBoxSizer, flag=wx.ALIGN_BOTTOM)

      return hButtonBoxSizer

   def CreatePositionStatusControls(self):
      vBoxSizer = wx.BoxSizer(wx.VERTICAL)

      # add status controls
      spinText = wx.StaticText(self, -1, "Step size  ")
      vBoxSizer.Add(spinText,0 , flag=wx.ALIGN_CENTER_VERTICAL)

      self.spinCtrl = fs.FloatSpin(self, -1,
         min_val=0, max_val=99999, increment=0.10, value=1.0,
         agwStyle=fs.FS_LEFT)
      self.spinCtrl.SetFormat("%f")
      self.spinCtrl.SetDigits(4)

      vBoxSizer.Add(self.spinCtrl, 0,
         flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, border=5)

      spinText = wx.StaticText(self, -1, "Jog status  ")
      vBoxSizer.Add(spinText, 0, flag=wx.ALIGN_CENTER_VERTICAL)

      flexGridSizer = wx.FlexGridSizer(4,2,1,3)
      vBoxSizer.Add(flexGridSizer,0 , flag=wx.ALL|wx.EXPAND, border=5)

      # Add X pos
      st = wx.StaticText(self, label="X")
      self.jX = wx.TextCtrl(self, value=gc.gZeroString)
      flexGridSizer.Add(st, 0, flag=wx.ALIGN_CENTER_VERTICAL)
      flexGridSizer.Add(self.jX, 1, flag=wx.EXPAND)

      # Add Y Pos
      st = wx.StaticText(self, label="Y")
      self.jY = wx.TextCtrl(self, value=gc.gZeroString)
      flexGridSizer.Add(st, 0, flag=wx.ALIGN_CENTER_VERTICAL)
      flexGridSizer.Add(self.jY, 1, flag=wx.EXPAND)

      # Add Z Pos
      st = wx.StaticText(self, label="Z")
      self.jZ = wx.TextCtrl(self, value=gc.gZeroString)
      flexGridSizer.Add(st, 0, flag=wx.ALIGN_CENTER_VERTICAL)
      flexGridSizer.Add(self.jZ, 1, flag=wx.EXPAND)

      # Add Spindle status
      st = wx.StaticText(self, label="SP")
      self.jSpindle = wx.TextCtrl(self, value=gc.gOffString, style=wx.TE_READONLY)
      self.jSpindle.SetBackgroundColour(gc.gReadOnlyBkColor)
      flexGridSizer.Add(st, 0, flag=wx.ALIGN_CENTER_VERTICAL)
      flexGridSizer.Add(self.jSpindle, 1, flag=wx.EXPAND)

      # Add Checkbox for sync with work position
      self.useWorkPosCheckBox = wx.CheckBox (self, label="Auto MPOS")
      self.useWorkPosCheckBox.SetValue(self.configAutoMPOS)
      self.useWorkPosCheckBox.SetToolTip(
         wx.ToolTip("Use Machine position to update Jogging position, "\
            "jogging operation use these values to operate"))
      self.Bind(wx.EVT_CHECKBOX, self.OnUseMachineWorkPosition, self.useWorkPosCheckBox)
      vBoxSizer.Add(self.useWorkPosCheckBox)

      return vBoxSizer

   def CreateGotoAndResetControls(self):
      vBoxSizer = wx.BoxSizer(wx.VERTICAL)

      # Add radio buttons
      spinText = wx.StaticText(self, -1, "Select axis (f)")
      vBoxSizer.Add(spinText,0 , flag=wx.ALIGN_CENTER_VERTICAL)

      vRadioBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
      self.xCheckBox = wx.CheckBox(self, label='X')
      vRadioBoxSizer.Add(self.xCheckBox, flag=wx.LEFT|wx.EXPAND, border=5)
      self.Bind(wx.EVT_CHECKBOX, self.OnXCheckBox, self.xCheckBox)

      self.yCheckBox = wx.CheckBox(self, label='Y')
      vRadioBoxSizer.Add(self.yCheckBox, flag=wx.LEFT|wx.EXPAND, border=5)
      self.Bind(wx.EVT_CHECKBOX, self.OnYCheckBox, self.yCheckBox)

      self.zCheckBox = wx.CheckBox(self, label='Z')
      vRadioBoxSizer.Add(self.zCheckBox, flag=wx.LEFT|wx.EXPAND, border=5)
      self.Bind(wx.EVT_CHECKBOX, self.OnZCheckBox, self.zCheckBox)

      self.allCheckBox = wx.CheckBox(self, label='All')
      vRadioBoxSizer.Add(self.allCheckBox, flag=wx.LEFT|wx.EXPAND, border=5)
      self.Bind(wx.EVT_CHECKBOX, self.OnAllCheckBox, self.allCheckBox)

      vBoxSizer.Add(vRadioBoxSizer, 0, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER)

      # Add Buttons
      spinText = wx.StaticText(self, -1, "Operation on (f)")
      vBoxSizer.Add(spinText,0 , flag=wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.EXPAND, border=5)

      # Add reset and move to zero(0) buttons
      vButtonBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

      self.resetToZeroButton = wx.Button(self, label="f = 0")
      self.resetToZeroButton.SetToolTip(wx.ToolTip("Set f axis to zero(0)"))
      self.Bind(wx.EVT_BUTTON, self.OnResetToZero, self.resetToZeroButton)
      vButtonBoxSizer.Add(self.resetToZeroButton, flag=wx.TOP|wx.EXPAND)#, border=5)

      self.gotoToZeroButton = wx.Button(self, label="f -> 0")
      self.gotoToZeroButton.SetToolTip(wx.ToolTip("Move f axis to zero(0)"))
      self.Bind(wx.EVT_BUTTON, self.OnGoToZero, self.gotoToZeroButton)
      vButtonBoxSizer.Add(self.gotoToZeroButton, flag=wx.TOP|wx.EXPAND)#, border=5)

      vBoxSizer.Add(vButtonBoxSizer, flag=wx.TOP|wx.EXPAND, border=5)

      # Add reset and move to jog buttons
      vButtonBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

      self.resetToJogButton = wx.Button(self, label="f = Jog(f)")
      self.resetToJogButton.SetToolTip(wx.ToolTip("Set f axis to Jog(f) current value"))
      self.Bind(wx.EVT_BUTTON, self.OnResetToJogVal, self.resetToJogButton)
      vButtonBoxSizer.Add(self.resetToJogButton, flag=wx.TOP|wx.EXPAND)#, border=5)

      self.gotoToJogButton = wx.Button(self, label="f -> Jog(f)")
      self.gotoToJogButton.SetToolTip(wx.ToolTip("Move f axis to Jog(f) current value"))
      self.Bind(wx.EVT_BUTTON, self.OnGoToJogVal, self.gotoToJogButton)
      vButtonBoxSizer.Add(self.gotoToJogButton, flag=wx.TOP|wx.EXPAND)#, border=5)

      vBoxSizer.Add(vButtonBoxSizer, flag=wx.TOP|wx.EXPAND)#, border=5)

      # Add move home buttons
      self.gotoToHomeButton = wx.Button(self, label="f -> Home")
      self.gotoToHomeButton.SetToolTip(wx.ToolTip("Move f axis HOME"))
      self.Bind(wx.EVT_BUTTON, self.OnGoHome, self.gotoToHomeButton)
      vBoxSizer.Add(self.gotoToHomeButton, flag=wx.TOP|wx.EXPAND)#, border=5)


      spinText = wx.StaticText(self, -1, "Jog memory stack")
      vBoxSizer.Add(spinText,0 , flag=wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.EXPAND, border=5)

      # add jog position memory stack
      hBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

      self.pushStackButton = wx.Button(self, label="+", style=wx.BU_EXACTFIT)
      self.pushStackButton.SetToolTip(
         wx.ToolTip("Adds current jog position values to jog memory stack"))
      self.Bind(wx.EVT_BUTTON, self.OnPushStack, self.pushStackButton)
      hBoxSizer.Add(self.pushStackButton, 1, flag=wx.EXPAND)

      self.jogMemoryStackComboBox = wx.combo.BitmapComboBox(self, -1, value="", size=(10,-1),
         choices=[], style=wx.CB_READONLY|wx.CB_DROPDOWN)
      self.jogMemoryStackComboBox.SetToolTip(wx.ToolTip("jog memory stack"))
      self.Bind(wx.EVT_COMBOBOX, self.OnPopStack, self.jogMemoryStackComboBox)
      hBoxSizer.Add(self.jogMemoryStackComboBox, 2, flag=wx.EXPAND)

      vBoxSizer.Add(hBoxSizer, flag=wx.TOP|wx.EXPAND, border=5)

      return vBoxSizer

   def CreateUtilControls(self):
      vBoxSizer = wx.BoxSizer(wx.VERTICAL)

      spinText = wx.StaticText(self, -1, "Custom buttons")
      vBoxSizer.Add(spinText,0 , flag=wx.ALIGN_CENTER_VERTICAL)

      # add custom buttons
      hBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

      self.custom1Button = wx.Button(self, label=self.configCustom1Label)
      self.custom1Button.SetToolTip(wx.ToolTip("Move to pre-defined position (1)"))
      self.Bind(wx.EVT_BUTTON, self.OnCustom1Button, self.custom1Button)
      hBoxSizer.Add(self.custom1Button, flag=wx.TOP|wx.EXPAND, border=5)

      self.custom2Button = wx.Button(self, label=self.configCustom2Label)
      self.custom2Button.SetToolTip(wx.ToolTip("Move to pre-defined position (2)"))
      self.Bind(wx.EVT_BUTTON, self.OnCustom2Button, self.custom2Button)
      hBoxSizer.Add(self.custom2Button, flag=wx.TOP|wx.EXPAND, border=5)

      self.custom3Button = wx.Button(self, label=self.configCustom3Label)
      self.custom3Button.SetToolTip(wx.ToolTip("Move to pre-defined position (3)"))
      self.Bind(wx.EVT_BUTTON, self.OnCustom3Button, self.custom3Button)
      hBoxSizer.Add(self.custom3Button, flag=wx.TOP|wx.EXPAND, border=5)

      self.custom4Button = wx.Button(self, label=self.configCustom4Label)
      self.custom4Button.SetToolTip(wx.ToolTip("Move to pre-defined position (4)"))
      self.Bind(wx.EVT_BUTTON, self.OnCustom4Button, self.custom4Button)
      hBoxSizer.Add(self.custom4Button, flag=wx.TOP|wx.EXPAND, border=5)

      vBoxSizer.Add(hBoxSizer, flag=wx.EXPAND)

      return vBoxSizer

   def AxisJog(self, staticControl, axis, opAdd):
      fAxisPos = float(staticControl.GetValue())

      if opAdd:
         fAxisPos += self.spinCtrl.GetValue()
      else:
         fAxisPos -= self.spinCtrl.GetValue()

      fAxisStrPos = gc.gNumberFormatString % (fAxisPos)
      staticControl.SetValue(fAxisStrPos)

      cmd = "".join([gc.gDEVICE_CMD_GO_TO_POS, " ", axis, str(fAxisStrPos), "\n"])
      self.mainWindow.SerialWriteWaitForAck(cmd)

   def OnAllCheckBox(self, evt):
      self.xCheckBox.SetValue(evt.IsChecked())
      self.yCheckBox.SetValue(evt.IsChecked())
      self.zCheckBox.SetValue(evt.IsChecked())

   def OnXCheckBox(self, evt):
      if evt.IsChecked() and self.yCheckBox.IsChecked() and self.zCheckBox.IsChecked():
         self.allCheckBox.SetValue(True)
      else:
         self.allCheckBox.SetValue(False)

   def OnYCheckBox(self, evt):
      if evt.IsChecked() and self.xCheckBox.IsChecked() and self.zCheckBox.IsChecked():
         self.allCheckBox.SetValue(True)
      else:
         self.allCheckBox.SetValue(False)

   def OnZCheckBox(self, evt):
      if evt.IsChecked() and self.xCheckBox.IsChecked() and self.yCheckBox.IsChecked():
         self.allCheckBox.SetValue(True)
      else:
         self.allCheckBox.SetValue(False)

   def OnXPos(self, e):
      self.AxisJog(self.jX, "X", opAdd=True)

   def OnXNeg(self, e):
      self.AxisJog(self.jX, "X", opAdd=False)

   def OnYPos(self, e):
      self.AxisJog(self.jY, "Y", opAdd=True)

   def OnYNeg(self, e):
      self.AxisJog(self.jY, "Y", opAdd=False)

   def OnZPos(self, e):
      self.AxisJog(self.jZ, "Z", opAdd=True)

   def OnZNeg(self, e):
      self.AxisJog(self.jZ, "Z", opAdd=False)

   def OnSpindleOn(self, e):
      self.jSpindle.SetValue(gc.gOnString)
      self.mainWindow.SerialWriteWaitForAck("".join(
         [gc.gDEVICE_CMD_SPINDLE_ON, "\n"]))

   def OnSpindleOff(self, e):
      self.jSpindle.SetValue(gc.gOffString)
      self.mainWindow.SerialWriteWaitForAck("".join(
         [gc.gDEVICE_CMD_SPINDLE_OFF, "\n"]))

   def OnUseMachineWorkPosition(self, e):
      self.configAutoMPOS = e.IsChecked()

   def OnJogCmd (self, xval, yval, zval, gcode_cmd):
      cmd = ""
      cmdx = ""
      cmdy = ""
      cmdz = ""


      if self.xCheckBox.GetValue() or self.allCheckBox.GetValue():
         self.jX.SetValue(xval)
         cmdx = " X%s" % xval

      if self.yCheckBox.GetValue() or self.allCheckBox.GetValue():
         self.jY.SetValue(yval)
         cmdy = " Y%s" % yval

      if self.zCheckBox.GetValue() or self.allCheckBox.GetValue():
         self.jZ.SetValue(zval)
         cmdz = " Z%s" % zval

      if (len(cmdx) > 0) or (len(cmdy) > 0) or (len(cmdz) > 0):
         cmd = "".join([gcode_cmd, cmdx, cmdy, cmdz, "\n"])

      if len(cmd) > 1:
         self.mainWindow.SerialWriteWaitForAck(cmd)
      # else:
      # maybe we need to show a hint (did you you forget to select an
      # axis

   def OnResetToZero(self, e):
      mim = mi.GetMachIfModule(self.stateData.machIfId)

      self.OnJogCmd(gc.gZeroString, gc.gZeroString, gc.gZeroString,
            mim.GetSetAxisCmd())

      if self.configReqUpdateOnJogSetOp:
         self.mainWindow.GetMachineStatus()

   def OnGoToZero(self, e):
      self.OnJogCmd(gc.gZeroString, gc.gZeroString, gc.gZeroString,
         gc.gDEVICE_CMD_GO_TO_POS)

   def OnResetToJogVal(self, e):
      mim = mi.GetMachIfModule(self.stateData.machIfId)

      self.OnJogCmd(
         self.jX.GetValue(), self.jY.GetValue(), self.jZ.GetValue(),
         mim.GetSetAxisCmd())

      if self.configReqUpdateOnJogSetOp:
         self.mainWindow.GetMachineStatus()


   def OnGoToJogVal(self, e):
      self.OnJogCmd(
         self.jX.GetValue(), self.jY.GetValue(), self.jZ.GetValue(),
         gc.gDEVICE_CMD_GO_TO_POS)

   def OnGoHome(self, e):
      self.OnJogCmd(gc.gZeroString, gc.gZeroString, gc.gZeroString,
         gc.gDEVICE_CMD_HOME_AXIS)

   def OnPushStack(self, e):
      xVal = self.jX.GetValue()
      yVal = self.jY.GetValue()
      zVal = self.jZ.GetValue()

      self.jogMemoryStackComboBox.Append("X%s,Y%s,Z%s" % (xVal, yVal, zVal))

   def OnPopStack(self, e):
      strXYZ = self.jogMemoryStackComboBox.GetValue()
      self.jX.SetValue(re.search("X(\S+),Y", strXYZ).group(1))
      self.jY.SetValue(re.search("Y(\S+),Z", strXYZ).group(1))
      self.jZ.SetValue(re.search("Z(\S+)", strXYZ).group(1))

   def OnCustomButton(self, optPos, optScr, xo, xv, yo, yv, zo, zv, script):

      if optPos:
         fXPos = float(self.jX.GetValue())
         fYPos = float(self.jY.GetValue())
         fZPos = float(self.jZ.GetValue())
         fXVal = float(xv)
         fYVal = float(yv)
         fZVal = float(zv)

         fXnp = fXVal
         if xo:
            fXnp = fXPos + fXVal

         fYnp = fYVal
         if yo:
            fYnp = fYPos + fYVal

         fZnp = fZVal
         if zo:
            fZnp = fZPos + fZVal

         self.jX.SetValue(str(fXnp))
         self.jY.SetValue(str(fYnp))
         self.jZ.SetValue(str(fZnp))

         goPosCmd = "".join([gc.gDEVICE_CMD_GO_TO_POS, " X", str(fXnp),
            " Y", str(fYnp), " Z", str(fZnp)])
         self.mainWindow.SerialWriteWaitForAck(goPosCmd)

      if optScr:
         scriptLines = script.splitlines()

         if len(scriptLines) > 0:
            for scriptLine in scriptLines:
               scriptLine = "".join([scriptLine, "\n"])
               self.mainWindow.SerialWriteWaitForAck(scriptLine)

   def OnCustom1Button(self, e):
      self.OnCustomButton(
         self.configCustom1OptPosition, self.configCustom1OptScript,
         self.configCustom1XIsOffset, self.configCustom1XValue,
         self.configCustom1YIsOffset, self.configCustom1YValue,
         self.configCustom1ZIsOffset, self.configCustom1ZValue,
         self.configCustom1Script
      )

   def OnCustom2Button(self, e):
      self.OnCustomButton(
         self.configCustom2OptPosition, self.configCustom2OptScript,
         self.configCustom2XIsOffset, self.configCustom2XValue,
         self.configCustom2YIsOffset, self.configCustom2YValue,
         self.configCustom2ZIsOffset, self.configCustom2ZValue,
         self.configCustom2Script
      )

   def OnCustom3Button(self, e):
      self.OnCustomButton(
         self.configCustom3OptPosition, self.configCustom3OptScript,
         self.configCustom3XIsOffset, self.configCustom3XValue,
         self.configCustom3YIsOffset, self.configCustom3YValue,
         self.configCustom3ZIsOffset, self.configCustom3ZValue,
         self.configCustom3Script
      )

   def OnCustom4Button(self, e):
      self.OnCustomButton(
         self.configCustom4OptPosition, self.configCustom4OptScript,
         self.configCustom4XIsOffset, self.configCustom4XValue,
         self.configCustom4YIsOffset, self.configCustom4YValue,
         self.configCustom4ZIsOffset, self.configCustom4ZValue,
         self.configCustom4Script
      )

   def OnRefresh(self, e):
      pass

   def GetCliCommand(self):
      return self.cliCommand

   def OnCliEnter(self, e):
      cliCommand = self.cliComboBox.GetValue()

      if cliCommand != self.cliCommand:
         if self.cliComboBox.GetCount() > self.cliCmdMaxHistory:
            self.cliComboBox.Delete(0)

         self.cliCommand = cliCommand
         self.cliComboBox.Append(self.cliCommand)

      self.cliComboBox.SetValue("")

      self.cliIndex = self.cliComboBox.GetCount()
      e.Skip()

   def OnCliKeyDown(self, e):
      keyCode = e.GetKeyCode()
      cliItems = self.cliComboBox.GetItems()

      if wx.WXK_UP == keyCode or wx.WXK_NUMPAD_UP == keyCode:
         if  self.cliIndex > 0:
            self.cliIndex = self.cliIndex - 1
            self.cliComboBox.SetValue(cliItems[self.cliIndex])
      elif wx.WXK_DOWN == keyCode or wx.WXK_NUMPAD_DOWN == keyCode:
         if  len(cliItems) > self.cliIndex + 1:
            self.cliIndex = self.cliIndex + 1
            self.cliComboBox.SetValue(cliItems[self.cliIndex])
      else:
         e.Skip()

   def LoadCli(self):
      # read cmd hsitory
      configData = self.cliCmdHistory
      if len(configData) > 0:
         cliCommandHistory = configData.split("|")
         for cmd in cliCommandHistory:
            cmd = cmd.strip()
            if len(cmd) > 0:
               self.cliComboBox.Append(cmd.strip())

         self.cliCommand = cliCommandHistory[len(cliCommandHistory) - 1]
         self.cliIndex = self.cliComboBox.GetCount()

   def SaveCli(self):
      # write cmd history
      if self.cliSaveCmdHistory:
         cliCmdHistory = self.cliComboBox.GetItems()
         if len(cliCmdHistory) > 0:
            cliCmdHistory =  "|".join(cliCmdHistory)
            self.configData.Set('/cli/CmdHistory', cliCmdHistory)
