from openerp import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def copy(self, default=None):  # pylint: disable=W0622
        if not default:
            default = {}
        default['hrsft_ice'] = ""
        return super(ResPartner, self).copy(default=default)

    _sql_constraints = [
        ('hrsft_ice_unique', 'UNIQUE(hrsft_ice)', " Le champ ICE est deja existant !!"),
    ]