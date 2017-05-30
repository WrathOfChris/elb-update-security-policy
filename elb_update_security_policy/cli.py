import fnmatch
import re
import sys
import time
from .util import common_parser, common_args, catch_sigint
from .UpdateSecurityPolicy import UpdateSecurityPolicy


def elb_update_security_policy():
    exitcode = 0
    policyprefix = 'CLI-SSLNegotiationPolicy'
    catch_sigint()
    parser = common_parser('ELB Update Security Policy')

    parser.add_argument(
            '--old',
            help='old security-policy-name'
            )
    parser.add_argument(
            '--new',
            help='new security-policy-name',
            required=True
            )
    parser.add_argument(
            '--regex',
            help='use regex instead of simple match',
            action='store_true'
            )
    parser.add_argument(
            'elb',
            metavar='ELB',
            nargs='+',
            type=str,
            help='list of ELBs or regexes to match'
            )

    args = parser.parse_args()
    common_args(args)

    rc = UpdateSecurityPolicy(args.region)
    elbs = rc.get_all_elbs()
    sys.stdout.write('found %i elbs\n\n' % len(elbs))
    timestamp = int(time.time())

    for elb in elbs:
        # Match ELB names
        matches = 0
        for r in args.elb:
            if args.regex:
                match = re.match(r, elb.name)
            else:
                match = fnmatch.fnmatch(elb.name, r)
            if match:
                matches += 1

        if matches == 0:
            continue

        policyexists = False
        policyname = args.new
        for p in elb.policies.other_policies:
            if p.policy_name == args.new:
                policyexists = True
        if not policyexists:
            # AWSConsole uses format:
            # AWSConsole-SSLNegotiationPolicy-wrathoftest-stage-1425581270107
            policyname = '%s-%s-%s' % (policyprefix, elb.name, timestamp)
            sys.stdout.write('create elb %s policy %s ref %s\n' \
                    % (elb.name, policyname, args.new))
            ret = rc.create_policy(elb.name, policyname, args.new)
            if ret is False:
                exitcode = 1
                sys.stdout.write('failed creating elb %s policy %s ref %s\n' \
                        % (elb.name, policyname, args.new))
                continue

        for l in elb.listeners:
            for p in l.policy_names:
                if not args.old or p == args.old:
                    sys.stdout.write('update elb %s port %d\n' % (
                        elb.name,
                        l.load_balancer_port
                        ))
                    ret = rc.update_elb(
                            elb.name,
                            l.load_balancer_port,
                            policyname
                            )
                    if ret is False:
                        exitcode = 1

    sys.exit(exitcode)
