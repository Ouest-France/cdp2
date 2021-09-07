import subprocess
import logging, verboselogs
import os

LOG = verboselogs.VerboseLogger('dockercommand')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)

class MavenCommand(object):

    def __init__(self, cmd, docker_image ):
        self._cmd = cmd
        self._docker_image = docker_image
        self._with_entrypoint = False
        self._cmd.run_command('docker pull %s' % docker_image)

    @staticmethod
    def get_command(prg_cmd, docker_image):
        run_docker_cmd = 'docker run --rm -e DOCKER_HOST'

        for env in os.environ:
            if env.startswith('CI') or env.startswith('CDP') or env.startswith('AWS') or env.startswith('GIT') or env.startswith('KUBERNETES'):
                run_docker_cmd = '%s -e %s' % (run_docker_cmd, env)
      
        run_docker_cmd = '%s -v $PWD:$PWD' % (run_docker_cmd)
        run_docker_cmd = '%s -w %s' % (run_docker_cmd, '${PWD}')
        run_docker_cmd = '%s %s' % (run_docker_cmd, docker_image)
        run_docker_cmd = '%s /bin/sh -c \'%s\'' % (run_docker_cmd, prg_cmd)
        return run_docker_cmd

    def run(self, prg_cmd):
        run_docker_cmd = MavenCommand.get_command(prg_cmd,self._docker_image)

        LOG.info('')
        LOG.info('******************** Docker command ********************')
        LOG.info('Image: %s' % self._docker_image)
        LOG.info('Command: %s' % prg_cmd)
        LOG.verbose(run_docker_cmd)

        return self._cmd.run(run_docker_cmd, None, None)