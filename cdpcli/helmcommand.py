import subprocess
import logging, verboselogs
import os

LOG = verboselogs.VerboseLogger('dockercommand')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)

class HelmCommand(object):

    def __init__(self, cmd, version, with_entrypoint = False):
        self._cmd = cmd
        self._version = version
        self._with_entrypoint = with_entrypoint

    def run(self, prg_cmd, dry_run = None, timeout = None, workingDir = True):
        prg_cmd = '%s %s' % ("helm3" if self._version == "3" else "helm2", prg_cmd)

        LOG.info('')
        LOG.info('******************** command ********************')
        LOG.info('Version: %s' % self._version)
        LOG.info('Command: %s' % prg_cmd)

        return self._cmd.run(prg_cmd, dry_run=dry_run, timeout=timeout)
