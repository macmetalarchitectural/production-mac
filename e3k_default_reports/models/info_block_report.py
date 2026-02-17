from odoo import models


class SaleOrderReport(models.AbstractModel):
    _name = 'info.block.report.mixin'
    _description = 'Information block Report mixin'

    def information_block_to_display(self):
        """
        Retourne un dictionnaire contenant les informations principales de la
        commande à afficher dans un bloc d'information.

        Format retourné :
            {
                'clé': {
                    'label': str,   # Libellé affiché
                    'value': Any,   # Valeur de l'attribut ou False si non défini
                    'type': str     # Type de donnée ('string' ou 'date')
                },
                ...
            }

        Chaque
        """
        raise NotImplementedError("La méthode _get_informations_blocks doit être implémentée dans les classes enfants.")

    def get_info_block_report_values(self, row_size):
        """
        Génère une liste de lignes contenant les blocs d'informations à afficher dans le rapport.

        Args:
            row_size (int): Nombre d'éléments par ligne.

        Returns:
            list: Liste de listes, chaque sous-liste représentant une ligne de blocs d'informations.

        Cette méthode organise les blocs d'informations retournés par `information_block_to_display`
        en lignes de taille maximale `row_size`. Les blocs dont la valeur est vide sont ignorés.
        """
        rows = []
        current_row = []
        self.ensure_one()

        def add_to_row(item):
            current_row.append(item)
            if len(current_row) == row_size and current_row:
                rows.append(current_row.copy())
                current_row.clear()

        for field, data in self.information_block_to_display().items():
            if data['value']:
                add_to_row(data)
        if current_row and row_size:
            rows.append(current_row)

        return rows
