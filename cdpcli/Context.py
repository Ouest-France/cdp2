#!/usr/bin/env python2.7

from __future__ import absolute_import
import os
import re
import json
import base64
from .awscommand import AwsCommand

class Context(object):

    def __init__(self, opt, cmd, LOG):
        self._opt = opt
        self._cmd = cmd
        self._registry = None
        self.auths = {}
        self.auths["auths"] = {}

        registries = [["--use-custom-registry","artifactory"],["--use-gitlab-registry","gitlab"],["--use-aws-ecr","aws-ecr"]]
        for registry in registries:
            if opt[registry[0]] :
                LOG.warning("\x1b[31;1mWARN : Option %s is DEPRECATED. Use --use-registry=%s instead. Set to %s\x1b[0m",registry[0],registry[1],registry[1] )
                opt["--use-registry"] = registry[1]

        if opt['--put'] or opt['--delete']:
            self._registry = os.environ['CI_REGISTRY']

        if opt['--login-registry'] and opt['--login-registry'] != opt['--use-registry']:
            if opt['--login-registry'] == 'aws-ecr':
                aws_cmd = AwsCommand(cmd, "", True)
                login_regex = re.findall('docker login -u (.*) -p (.*) https://(.*)', aws_cmd.run('ecr get-login --no-include-email --cli-read-timeout 30 --cli-connect-timeout 30', dry_run=False)[0].strip())
                self._registry = login_regex[0][2]
                self._registry_user_ro = login_regex[0][0]
                self._registry_token_ro = login_regex[0][1]
                # Login AWS registry
                self.__login(self._registry, self._registry_user_ro,self._registry_token_ro)
            else:
                self.__login(os.getenv('CDP_%s_REGISTRY' % opt['--login-registry'].upper(), None),
                             os.getenv('CDP_%s_REGISTRY_USER' % opt['--login-registry'].upper(), None),
                             os.getenv('CDP_%s_REGISTRY_TOKEN' % opt['--login-registry'].upper(), None))

        # Login to Dockerhub if needed
        self.__loginDockerhub()

        if opt['--use-registry'] != 'none':
            if opt['maven'] or opt['docker'] or opt['k8s']:
                if opt['--use-registry'] == 'aws-ecr' :
                    ### Get login from AWS-CLI
                    aws_cmd = AwsCommand(cmd, "", True)
                    login_regex = re.findall('docker login -u (.*) -p (.*) https://(.*)', aws_cmd.run('ecr get-login --no-include-email --cli-read-timeout 30 --cli-connect-timeout 30', dry_run=False)[0].strip())
                    self._registry = login_regex[0][2]
                    self._registry_user_ro = login_regex[0][0]
                    self._registry_token_ro = login_regex[0][1]
                    # Login AWS registry
                    self.__login(self._registry, self._registry_user_ro,self._registry_token_ro)

                elif opt['--use-registry'] == 'gitlab' :
                    # Use gitlab registry
                    self.__set_registry(os.getenv('CI_REGISTRY', None),
                                        os.getenv('CI_DEPLOY_USER', None),
                                        os.getenv('CI_DEPLOY_PASSWORD', None))
                    # Login gitlab registry
                    self.__login(os.getenv('CI_REGISTRY', None),
                                 os.getenv('CI_REGISTRY_USER', None),
                                 os.getenv('CI_JOB_TOKEN', None))
                else:
                    ### Used by '--use-registry' params
                    registry = opt['--use-registry'].upper()
                    self.__set_registry(os.getenv('CDP_%s_REGISTRY' % registry,None),
                                        self.getRegistryReadOnlyUser(registry),
                                        os.getenv('CDP_%s_REGISTRY_READ_ONLY_TOKEN' % registry,None))
                    self.__login(os.getenv('CDP_%s_REGISTRY' % registry, None),
                                 os.getenv('CDP_%s_REGISTRY_USER' % registry, None),
                                 os.getenv('CDP_%s_REGISTRY_TOKEN' % registry, None))


    def __set_registry(self,registry,user_ro,token_ro):
        self._registry = registry
        self._registry_user_ro = user_ro
        self._registry_token_ro = token_ro

    @property
    def opt(self):
        return self._opt

    @property
    def registry(self):
        return self._registry

    @property
    def registry_user_ro(self):
        return self.__verif_attr(self._registry_user_ro)

    @property
    def registry_token_ro(self):
        return self.__verif_attr(self._registry_token_ro)

    @property
    def image_name(self):
        # Configure docker registry
        image_name = self.opt['--image-name'] if self.opt['--image-name'] else self.project_name
        return image_name

    @property
    def full_image_path(self):
        return "%s/%s/%s" % (self.registry, self.repository, self.image_name)

    @property
    def root_repository(self):
        return self.opt['--image-repository'] if self.opt['--image-repository'] else ( self.project_name if self.opt['--use-registry']=="harbor" else os.environ['CI_PROJECT_PATH'])

    @property
    def repository(self):
        root_repo = self.root_repository
        subrepo=""
        if self.opt['--image-name']:
           subrepo = "/" + self.opt['--image-name']
        else:
            if (self.opt['--use-registry']=="harbor") and not self.isMultiBuildContext():
              subrepo = "/" + self.project_name
        if self.opt['--docker-build-target']:
          subrepo = '%s/%s' % (subrepo, self.opt['--docker-build-target'])

        return root_repo + subrepo


    @property
    # Retourne le repo + le nom de l'image
    # Dans le cas d'un multi-build, ne retourne que le repo pour retrocompatibilité 
    def registryImagePath(self):
        repository = self.repository
        return repository

    def isMultiBuildContext(self):
        return os.path.isfile(self.opt['--build-file'])

    @property
    def project_name(self):
        return os.environ['CI_PROJECT_NAME'].lower()

    @property
    def is_image_pull_secret(self):
        image_pull_secret =  os.getenv('CDP_IMAGE_PULL_SECRET', None)
        if image_pull_secret is not None:
            return True if image_pull_secret == 'true' else False
        else:
            return self.opt['--image-pull-secret']

    def string_protected(selft,input):
        if not input.startswith("'"):
            input = "'"+input
        if not input.endswith("'"):
            input = input+"'"
        return input

    def __verif_attr(self, attr):
        if attr is None:
            raise ValueError('Compatible with gitlab >= 10.8 or deploy token with the name gitlab-deploy-token and the scope read_registry must be created in this project.')
        return attr

    def __loginDockerhub(self):
        registry_user = os.getenv('CDP_DOCKERHUB_REGISTRY_USER',None)
        registry_token = os.getenv('CDP_DOCKERHUB_READ_ONLY_TOKEN',None)
        registry_url = os.getenv('CDP_DOCKERHUB_REGISTRY_URL','https://index.docker.io/v1/')
        if registry_user is not None and registry_token is not None:
           self.__loginRegistry(registry_url, registry_user, registry_token)

    def __login(self, registry, registry_user, registry_token):
        # Activate login, only specific stage.
        if self._opt['maven'] or self._opt['docker'] or self._opt['k8s']:
            if registry_user is not None and registry_token is not None and registry is not None:
               self.__loginRegistry(registry, registry_user, registry_token)


    def __loginRegistry(self, registry, registry_user, registry_token):
          auth = registry_user + ":" + registry_token
          encodedBytes = base64.b64encode(auth.encode("ascii"))
          encodedStr = str(encodedBytes, "ascii")

          self.auths["auths"][registry] = {"auth": encodedStr}
          self._cmd.run_secret_command("echo '%s' > ~/.docker/config.json" % ( json.dumps(self.auths)))

    ## Get option passed in command line or env variable if not set. Env variable is the upper param prefixed by CDP_ and dash replaced by underscore
    def getParamOrEnv(self, param, defaultValue = None):
        envvar = "CDP_%s" % param.upper().replace("-","_")
        value = defaultValue
        try:
          commandlineParam = "--%s" % param
          if self._opt[commandlineParam]:
              value = self._opt[commandlineParam]
          else: 
            if (len(os.getenv(envvar, '')) > 0 ):
               value = os.getenv(envvar)        
        except KeyError: 
            value = defaultValue
        return value

    def getRegistryReadOnlyUser(self,registry):
        user_ro = os.getenv('CDP_%s_REGISTRY_READ_ONLY_USER' % registry,None)
        if (user_ro is None or user_ro == ''):
            # Pour retro-compatibilté
            user_ro = os.getenv('CDP_%s_REGISTRY_USER'% registry,None)

        return user_ro