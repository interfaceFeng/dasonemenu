# -*- coding: utf-8 -*-


import logging
from common.modulehelper import LanguageType
try:
    from collections import OrderedDict
except Exception:
    # python 2.6 or earlier use backport
    from ordereddict import OrderedDict
import yaml


log = logging.getLogger('setting')

class Settings(object):
    @classmethod
    def read(cls, yamlfile):
        try:
            infile = file(yamlfile, 'r')
            settings = yaml.load(infile)
            if settings is not None:
                return settings
            else:
                return OrderedDict()
        except Exception:
            if yamlfile is not None:
                import logging
                log.error("Unable to read YAML: %s" % yamlfile)
            log.debug("return empty orderedDict")
            return OrderedDict()



    @classmethod
    def write(cls, newvalues, tree=None, defaultsfile='settings.yaml',
              outfn='mysettings.yaml'):
        try:
            settings = cls.read(defaultsfile)
            settings.update(cls.read(outfn))
            settings.update(newvalues)
            outfile = file(outfn, 'w')
            yaml.dump(settings, outfile, default_flow_style=False)
            return True
        except Exception:
            log.debug("write into file %s fail, info is %s"%(outfn, newvalues))
            return False
