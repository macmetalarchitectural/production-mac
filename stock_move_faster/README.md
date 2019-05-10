Stock Move Faster
=================
This module makes the processing of stock moves faster.
It does so by limiting the use of cache to store computed fields.

When processing stock moves, the cache is filled and invalidated after every move.
Thus, Odoo behaves in O(n2) regarding the number of move lines in a picking or inventory adjustment.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
