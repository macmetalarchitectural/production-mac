/** @odoo-module **/

import { registry } from "@web/core/registry";
import { preferencesItem } from "@web/webclient/user_menu/user_menu_items";

const userMenuRegistry = registry.category("user_menuitems");

userMenuRegistry.remove('documentation', preferencesItem)
userMenuRegistry.remove('support', preferencesItem)
userMenuRegistry.remove('odoo_account', preferencesItem)