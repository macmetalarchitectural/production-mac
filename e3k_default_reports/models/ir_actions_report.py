from odoo import fields, models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    e3k_nb_block_infos_per_row = fields.Integer(
        string="Number of blocks per row",
        default=4,
        help="Number of information blocks to display per row in reports using the info.block.report.mixin mixin.",
    )

    def _get_rendering_context(self, report, docids, data):
        """
        Surcharge le contexte de rendu pour les rapports.

        Récupère le contexte de rendu via la méthode parente, puis ajoute le nombre de blocs d'informations
        à afficher par ligne dans les rapports utilisant le mixin `info.block.report.mixin`.

        :param report: Instance du rapport en cours de rendu.
        :param docids: Identifiants des documents à inclure dans le rapport.
        :param data: Dictionnaire de données de contexte.
        :return: Dictionnaire de contexte enrichi pour le rendu du rapport.
        """
        data = super()._get_rendering_context(report, docids, data)
        data['e3k_nb_block_infos_per_row'] = report.e3k_nb_block_infos_per_row
        return data
