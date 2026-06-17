import os
import subprocess, threading
import logging, verboselogs
import timeit

LOG = verboselogs.VerboseLogger('clicommand')
LOG.addHandler(logging.StreamHandler())


class CLICommand(object):

    def __init__(self, dry_run = 1, log_level = logging.INFO):
        self._dry_run = dry_run
        LOG.setLevel(log_level)
        LOG.verbose('Dry-run init %s' % self._dry_run)

    def run_command(self, command, dry_run = None, timeout = None, raise_error = True, no_test = False):
        LOG.info('')
        LOG.info('******************** Run command ********************')
        LOG.info(command)
        return self.run(command, dry_run, timeout, raise_error, no_test)

    def run_secret_command(self, command, dry_run = None, timeout = None, raise_error = True,  no_test = False):
        return self.run(command, dry_run, timeout, raise_error, no_test)
        
    def run(self, command, dry_run = None, timeout = None, raise_error = True, no_test = False):
        start = timeit.default_timer()
        process = None
        output = []
        if "CDP_DEBUG" in os.environ:
          LOG.verbose('******************** Run command (debug) ********************')
          LOG.verbose(command)

        if dry_run is None:
            real_dry_run = self._dry_run
        else:
            real_dry_run = dry_run

        def target():
            nonlocal process
            LOG.info('---------- Output ----------')
            # If dry-run option, no execute command
            if not real_dry_run:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                while True:
                    line = process.stdout.readline().decode('UTF-8')
                    if line.strip() == '' and process.poll() is not None:
                        break
                    if line:
                        output.append(line.strip())
                        LOG.info(line.rstrip('\n'))

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout if timeout is None else float(timeout))

        if thread.is_alive():
            process.terminate()
            thread.join()

        LOG.info('---------- Time: %s s' % (round(timeit.default_timer() - start, 3)))
        LOG.info('')
        LOG.verbose('---------- CLICommand output: %s' % output)
        LOG.verbose('')

        if raise_error and process is not None and process.returncode != 0:
            LOG.warning('---------- ERROR ----------')
            raise OSError(process.returncode,'Error code %s' % process.returncode)

        return output