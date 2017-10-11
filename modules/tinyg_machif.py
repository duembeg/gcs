"""----------------------------------------------------------------------------
   tinyg_machif.py

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
import re

try:
    import simplejson as json
except ImportError:
    import json

import modules.machif as mi


"""----------------------------------------------------------------------------
   MachIf_TinyG:

   Machine Interface TinyG class.

   ID = 1100
   Name = "TinyG"
   input buffer max size = 255
   input buffer init size = -1
   input buffer watermark = 90%

   Init buffer to (-1) when connecting it needs a initial '\n' that
   should not be counted

----------------------------------------------------------------------------"""
class MachIf_TinyG(mi.MachIf_Base):
   inputBufferMaxSize = 255
   inputBufferInitVal = -1
   inputBufferWatermarkPrcnt = 0.90

   # TinyG text ack, example  "ok>"
   reTinyGMachineAck = re.compile(r'.+ok>\s$')

   def __init__(self, cmd_line_options):
      super(MachIf_TinyG, self).__init__(cmd_line_options, 1100,
         "TinyG", self.inputBufferMaxSize, self.inputBufferInitVal,
         self.inputBufferWatermarkPrcnt)

      self.inputBufferPart = list()

   def decode(self, data):
      dataDict = {}

      try:
         dataDict = json.loads(data)

         if 'r' in dataDict:
            r = dataDict['r']

            # get footer response out to avoid digging out later
            if 'f' in r:
               f = r['f']
               dataDict['f'] = f

            # get status response out to avoid digging out later
            if 'sr' in r:
               sr = r['sr']
               dataDict['sr'] = sr

            # get version out to avoid digging out later
            if 'sys' in r:
               sys = r['sys']

               if 'fb' in sys:
                  r['fb'] = sys['fb']

               if 'fv' in sys:
                  r['fv'] = sys['fv']

         if 'sr' in dataDict:
            sr = dataDict['sr']

            if 'stat' in sr:
               status = sr['stat']

               if 0 == status:
                  sr['stat'] = 'Init'
               elif 1 == status:
                  sr['stat'] = 'Ready'
               elif 2 == status:
                  sr['stat'] = 'Alarm'
               elif 3 == status:
                  sr['stat'] = 'Stop'
               elif 4 == status:
                  sr['stat'] = 'End'
               elif 5 == status:
                  sr['stat'] = 'Run'
               elif 6 == status:
                  sr['stat'] = 'Hold'
               elif 7 == status:
                  sr['stat'] = 'Probe'
               elif 8 == status:
                  sr['stat'] = 'Run'
               elif 9 == status:
                  sr['stat'] = 'Home'

            # deal with old versions of g2core
            if 'mpox' in sr:
               sr['posx'] = sr['mpox']
            if 'mpoy' in sr:
               sr['posy'] = sr['mpoy']
            if 'mpoz' in sr:
               sr['posz'] = sr['mpoz']
            if 'mpoa' in sr:
               sr['posa'] = sr['mpoa']

         if 'f' in dataDict:
            f = dataDict['f']

            # remove buffer part freed from acked command
            bufferPart = f[2]
            self.inputBufferSize = self.inputBufferSize - bufferPart

            if (self.inputBufferSize < 0):
               self.inputBufferSize = 0

            if self.cmdLineOptions.vverbose:
               print "** MachIf_TinyG input buffer decode returned: %d, buffer size: %d, %.2f%% full" % \
                  (bufferPart, self.inputBufferSize, \
                  (100 * (float(self.inputBufferSize)/self.inputBufferMaxSize)))

         dataDict['ib'] = [self.inputBufferMaxSize, self.inputBufferSize]

      except:
         ack = self.reTinyGMachineAck.match(data)
         if ack is not None:
            dataDict['r'] = {"f":[1,0,0]}
         else:
            if self.cmdLineOptions.vverbose:
               print "** MachIf_TinyG cannot decode data!! [%s]." % data

      return dataDict

   def encode(self, data, bookeeping=True):
      data = data.encode('ascii')

      if data in [self.getCycleStartCmd(), self.getFeedHoldCmd()]:
         pass
      elif bookeeping:
         dataLen = len(data)
         self.inputBufferSize = self.inputBufferSize + dataLen

         if self.cmdLineOptions.vverbose:
            print "** MachIf_TinyG input buffer encode used: %d, buffer size: %d, %.2f%% full" % \
               (dataLen, self.inputBufferSize, \
               (100 * (float(self.inputBufferSize)/self.inputBufferMaxSize)))

      return data

   def getInitCommCmd (self):
      return '\n{"sys":null}\n'

   def getQueueFlushCmd (self):
      return "%\n"

   def getSetAxisCmd (self):
      return "G28.3"

   def getStatusCmd(self):
      return '{"sr":null}\n'

   def reset(self):
      super(MachIf_TinyG, self)._reset(self.inputBufferMaxSize,
         self.inputBufferInitVal, self.inputBufferWatermarkPrcnt)

      self.inputBufferPart = list()
