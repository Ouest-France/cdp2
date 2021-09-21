import subprocess
import logging, verboselogs
import os

LOG = verboselogs.VerboseLogger('podmancommand')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)

class PodmanCommand(object):

    def __init__(self, cmd):
        self._cmd = cmd

    def run(self, prg_cmd, dry_run = None, timeout = None, workingDir = True):
        prg_cmd = 'podman %s' % (prg_cmd)
        LOG.info('')
        LOG.info('******************** command ********************')
        LOG.info('Command: %s' % prg_cmd)

        return self._cmd.run(prg_cmd, dry_run=dry_run, timeout=timeout)



