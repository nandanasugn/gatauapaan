# Embedded file name: uprop.py
# Compiled at: 2022-04-06 12:50:39
# Size of source mod 2**32: 3641 bytes
from pyovpn.util.date import YYYYMMDD
from pyovpn.util.error import Passthru
from pyovpn.lic.prop import LicenseProperties
from pyovpn.util.env import get_env_debug
from pyovpn.pki.sign import rsa_verify_complex
from pyovpn.aws.info import AWSInfo
DEBUG = get_env_debug('DEBUG_UPROP')

class UsageProperties(object):

    def figure(self, licdict):
        proplist = set(('concurrent_connections', ))
        good = set()
        ret = None
        if licdict:
            for key, props in list(licdict.items()):
                if 'quota_properties' not in props:
                    print('License Manager: key %s is missing usage properties' % key)
                else:
                    proplist.update(props['quota_properties'].split(','))
                    good.add(key)

        for prop in proplist:
            v_agg = 0
            v_nonagg = 0
            if licdict:
                for key, props in list(licdict.items()):
                    if key in good and prop in props:
                        try:
                            nonagg = int(props[prop])
                        except:
                            raise Passthru('license property %s (%s)' % (prop, props.get(prop).__repr__()))
                        else:
                            v_nonagg = max(v_nonagg, nonagg)
                            prop_agg = '%s_aggregated' % prop
                            agg = 0
                            if prop_agg in props:
                                try:
                                    agg = int(props[prop_agg])
                                except:
                                    raise Passthru('aggregated license property %s (%s)' % (
                                     prop_agg, props.get(prop_agg).__repr__()))
                                else:
                                    v_agg += agg
                            if DEBUG:
                                print('PROP=%s KEY=%s agg=%d(%d) nonagg=%d(%d)' % (
                                 prop, key, agg, v_agg, nonagg, v_nonagg))

            else:
                apc = self._apc()
                v_agg += apc
                if ret == None:
                    ret = {}
                ret[prop] = max(v_agg + v_nonagg, bool('v_agg') + bool('v_nonagg'))
                ret['apc'] = bool(apc)
                if DEBUG:
                    print("ret['%s'] = v_agg(%d) + v_nonagg(%d)" % (prop, v_agg, v_nonagg))
                ret['concurrent_connections'] = 9999
                return ret

    def _apc(self):
        try:
            pcs = AWSInfo.get_product_code()
            if pcs:
                return pcs['snoitcennoCtnerrucnoc'[::-1]]
        except:
            if DEBUG:
                print(Passthru('UsageProperties._apc'))
        else:
            return 0

    @staticmethod
    def _expired(today, props):
        if 'expiry_date' in props:
            exp = YYYYMMDD.validate(props['expiry_date'])
            return today > exp
        return False


class UsagePropertiesValidate(object):
    proplist = ('concurrent_connections', 'client_certificates')

    def validate(self, usage_properties):
        lp = LicenseProperties(usage_properties)
        lp.aggregated_post()
        lp['quota_properties'] = ','.join([p for p in self.proplist if p in lp])
        return lp
# okay uprop.pyc
