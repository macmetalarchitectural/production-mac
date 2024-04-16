odoo.define('e3k_mac_contact_customisation.ActivityDashboard', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var ActionMenu = AbstractAction.extend({

        contentTemplate: 'ActivityDashboard',

        events: {
           'click #hoverDiv': 'onclick_hoverDiv',
            'click #hoverDiv1': 'onclick_hoverDiv1',
            'click #hoverDiv2': 'onclick_hoverDiv2',
            'click #hoverDiv3': 'onclick_hoverDiv3',
        },

        onclick_hoverDiv: function (ev) {
             $("#hiddenDiv").toggle();
             if ($("#team_up").is(":visible"))
                {
                    $("#team_up").hide();
                    $("#team_down").show();
                }
             else
                {
                    $("#team_up").show();
                    $("#team_down").hide();
                }
        },

        onclick_hoverDiv1: function (ev) {
             $("#hiddenDiv1").toggle();
             if ($("#rep_up").is(":visible"))
                {
                    $("#rep_up").hide();
                    $("#rep_down").show();
                }
             else
                {
                    $("#rep_up").show();
                    $("#rep_down").hide();
                }
        },

        onclick_hoverDiv2: function (ev) {
             $("#hiddenDiv2").toggle();
             if ($("#meeting_type_up").is(":visible"))
                {
                    $("#meeting_type_up").hide();
                    $("#meeting_type_down").show();
                }
             else
                {
                    $("#meeting_type_up").show();
                    $("#meeting_type_down").hide();
                }
        },

        onclick_hoverDiv3: function (ev) {
             $("#hiddenDiv3").toggle();
             if ($("#closed_up").is(":visible"))
                {
                    $("#closed_up").hide();
                    $("#closed_down").show();
                }
             else
                {
                    $("#closed_up").show();
                    $("#closed_down").hide();
                }
        },



        renderElement: function (ev) {
            var self = this;
            $.when(this._super())
                .then(function (ev) {

                $('#hoverDiv').trigger('click');
                $('#hoverDiv1').trigger('click');
                $('#hoverDiv2').trigger('click');
                $('#hoverDiv3').trigger('click');



                 rpc.query({
                        model: "calendar.event",
                        method: "get_activity_details",
                    }).then(function (result) {
                        var inner ='<table class="table table-sm table-sm">';
                        inner+= "<thread><tr style='background-color: silver;'><th><strong>Team</strong></th><th><strong>Rep</strong></th><th><strong>Company name</strong></th><th><strong>Contact</strong></th><th><strong>Customer type</strong></th><th><strong>Status</strong></th><th><strong>Meeting type</strong></th><th><strong>Activity quantity</strong></th><th><strong>Closed</strong></th></tr></thread>";
                        inner+='<tbody>';
                        for (var k = 0; k < result.length; k++) {
                            var team = result[k].team_name;
                            var rep = result[k].rep;
                            var company = result[k].company_name;
                            var contact = result[k].contact;
                            var meeting_type = result[k].meeting_type;
                            var activity_quantity = result[k].activity_quantity;
                            var customer_type = result[k].customer_type;
                            var status = result[k].status;
                           inner+= '<tr><td>'+team+'</td><td>'+rep+'</td><td>'+company+'</td><td>'+contact+'</td><td>'+customer_type+'</td><td>'+status+'</td><td>'+meeting_type+'</td><td>'+activity_quantity+'</td><td></td><td></td></tr>';
                            }
                        inner+='</tbody>';
                        inner+='</table>';
                        $('#activity_details').append(inner);
                        })


            rpc.query({
                        model: "calendar.event",
                        method: "get_teams",
                    })
                    .then(function (result) {
                        if (result[0]) {
                            var container = document.getElementById("activity_team");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "name";
                            checkbox.value = "all";

                            // Create a label for the checkbox
                            var label = document.createElement("label");
                            label.appendChild(checkbox);
                            label.appendChild(document.createTextNode("Select all"));

                            // Append the label to the container
                            container.appendChild(label);
                            container.appendChild(document.createElement("br"));

                            for (var k = 0; k < result.length; k++) {
                                var item = result[k].name;
                                var value = result[k].id;

                                // Create a checkbox element
                                var checkbox = document.createElement("input");
                                checkbox.type = "checkbox";
                                checkbox.name = "name";
                                checkbox.value = value;

                                // Create a label for the checkbox
                                var label = document.createElement("label");
                                label.appendChild(checkbox);
                                label.appendChild(document.createTextNode(item));

                                // Append the label to the container
                                container.appendChild(label);
                                container.appendChild(document.createElement("br"));
                            }
                        }
                    })

            rpc.query({
                        model: "calendar.event",
                        method: "get_rep",
                    })
                    .then(function (result) {
                        if (result[0]) {
                            var container = document.getElementById("activity_rep");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "name";
                            checkbox.value = "all";

                            // Create a label for the checkbox
                            var label = document.createElement("label");
                            label.appendChild(checkbox);
                            label.appendChild(document.createTextNode("Select all"));

                            // Append the label to the container
                            container.appendChild(label);
                            container.appendChild(document.createElement("br"));

                            for (var k = 0; k < result.length; k++) {
                                var item = result[k].name;
                                var value = result[k].user_id;

                                // Create a checkbox element
                                var checkbox = document.createElement("input");
                                checkbox.type = "checkbox";
                                checkbox.name = "name";
                                checkbox.value = value;

                                // Create a label for the checkbox
                                var label = document.createElement("label");
                                label.appendChild(checkbox);
                                label.appendChild(document.createTextNode(item));

                                // Append the label to the container
                                container.appendChild(label);
                                container.appendChild(document.createElement("br"));
                            }
                        }
                    })

            rpc.query({
                        model: "calendar.event",
                        method: "get_meeting_type",
                    })
                    .then(function (result) {
                        if (result[0]) {
                            var container = document.getElementById("activity_meeting_type");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "name";
                            checkbox.value = "all";

                            // Create a label for the checkbox
                            var label = document.createElement("label");
                            label.appendChild(checkbox);
                            label.appendChild(document.createTextNode("Select all"));

                            // Append the label to the container
                            container.appendChild(label);
                            container.appendChild(document.createElement("br"));

                            for (var k = 0; k < result.length; k++) {
                                var item = result[k].name;
                                var value = result[k].id;

                                // Create a checkbox element
                                var checkbox = document.createElement("input");
                                checkbox.type = "checkbox";
                                checkbox.name = "name";
                                checkbox.value = value;

                                // Create a label for the checkbox
                                var label = document.createElement("label");
                                label.appendChild(checkbox);
                                label.appendChild(document.createTextNode(item));

                                // Append the label to the container
                                container.appendChild(label);
                                container.appendChild(document.createElement("br"));
                            }
                        }
                    })


           });
        },
    });
    core.action_registry.add('activity_dashboard', ActionMenu);

});