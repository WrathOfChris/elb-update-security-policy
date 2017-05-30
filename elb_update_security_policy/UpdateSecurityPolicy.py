import boto
import boto.ec2.elb
import boto.utils
from boto.exception import BotoServerError
import sys
import time

class UpdateSecurityPolicy():
    """
    ELB Security Policy Update
    """

    def __init__(self, region):
        self.region = region
        self.rate_limit_delay = 5
        self.elb = boto.ec2.elb.connect_to_region(self.region)
        self.account_id = None

    def get_account_id(self):
        if not self.account_id:
            iam = boto.connect_iam()
            self.account_id = iam.get_user()['get_user_response']['get_user_result']['user']['arn'].split(':')[4]
        return self.account_id

    def get_all_elbs(self, marker=None, elbs=list()):
        elb_call = self.wrap_aws_call(
                self.elb.get_all_load_balancers,
                marker=marker
                )
        elbs.extend(elb_call)
        if elb_call.next_marker:
            marker = elb_call.next_marker
            return self.get_all_elbs(marker, elbs)

        return elbs

    def update_elb(self, name, port, new):
        try:
            ret = self.wrap_aws_call(
                    self.elb.set_lb_policies_of_listener,
                    name,
                    port,
                    new
                    )
        except BotoServerError as e:
            sys.stderr.write('failed updating elb %s port %s: %s\n' % (
                name, port, e))
            return False
        return ret

    def create_policy(self, name, policyname, refname):
        policyattributes = { 'Reference-Security-Policy': refname }
        try:
            ret = self.wrap_aws_call(
                    self.elb.delete_lb_policy,
                    name,
                    policyname
                    )
            ret = self.wrap_aws_call(
                    self.elb.create_lb_policy,
                    name,
                    policyname,
                    'SSLNegotiationPolicyType',
                    policyattributes
                    )
            ret = self.wrap_aws_call(
                    self.elb.set_lb_policies_of_listener,
                    name,
                    443,
                    policyname
                    )
        except BotoServerError as e:
            sys.stderr.write('failed creating elb %s policy %s: %s\n' % (
                name, policyname, e))
            return False
        return ret

    def wrap_aws_call(self, awsfunc, *args, **nargs):
        """
        Wrap AWS call with Rate-Limiting backoff
        Gratefully taken Netflix/security_monkey
        """
        attempts = 0

        while True:
            attempts = attempts + 1
            try:
                if self.rate_limit_delay > 0:
                    time.sleep(self.rate_limit_delay)

                retval = awsfunc(*args, **nargs)

                if self.rate_limit_delay > 0:
                    self.rate_limit_delay = self.rate_limit_delay / 2

                return retval

            except BotoServerError as e:
                if e.error_code == 'Throttling':
                    if self.rate_limit_delay == 0:
                        self.rate_limit_delay = 1
                        sys.stderr.write('rate-limited: attempt %d\n' % \
                                attempts)
                    elif self.rate_limit_delay < 100:
                        self.rate_limit_delay = self.rate_limit_delay * 2
                        sys.stderr.write('rate-limited: attempt %d\n' % \
                                attempts)
                    else:
                        raise e
                else:
                    raise e
