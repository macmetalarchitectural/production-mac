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
            'click #hoverDiv1': 'onclick_hoverDiv1',
            'click #hoverDiv2': 'onclick_hoverDiv2',
            'click #hoverDiv3': 'onclick_hoverDiv3',
            'click #hoverDiv4': 'onclick_hoverDiv4',
            'click #hoverDiv5': 'onclick_hoverDiv5',
            'change #activity_team': 'onclick_activity_details',
            'change #activity_rep': 'onclick_activity_details',
            'change #activity_meeting_type': 'onclick_activity_details',
            'change #open_closed': 'onclick_activity_details',
            'change #activity_status': 'onclick_activity_details',
            'click #from_date': 'onclick_from_date',
            'change #from_date': 'onclick_activity_details',
            'click #to_date': 'onclick_to_date',
            'change #to_date': 'onclick_activity_details',
        },


        onclick_hoverDiv1: function (ev) {
             $("#hiddenDiv1").toggle();
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

        onclick_hoverDiv2: function (ev) {
             $("#hiddenDiv2").toggle();
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

        onclick_hoverDiv3: function (ev) {
             $("#hiddenDiv3").toggle();
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

        onclick_hoverDiv4: function (ev) {
             $("#hiddenDiv4").toggle();
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

        onclick_hoverDiv5: function (ev) {
             $("#hiddenDiv5").toggle();
             if ($("#status_up").is(":visible"))
                {
                    $("#status_up").hide();
                    $("#status_down").show();
                }
             else
                {
                    $("#status_up").show();
                    $("#status_down").hide();
                }
        },

        onclick_from_date: function (ev) {
            if (!document.getElementById("from_date").value) {
                var currentDate = new Date();
                // Set the time to 00:00:00
                currentDate.setHours(0, 0, 0, 0);
                // Adjust for the time zone offset
                var timezoneOffset = currentDate.getTimezoneOffset();
                currentDate.setMinutes(currentDate.getMinutes() - timezoneOffset);
                // Format the date to be compatible with the datetime-local input
                var formattedDate = currentDate.toISOString().slice(0, -8);
                document.getElementById("from_date").value = formattedDate;
                }
        },

        onclick_to_date: function (ev) {
            if (!document.getElementById("to_date").value) {
                var currentDate = new Date();
                // Set the time to 23:59:59
                currentDate.setHours(23, 59, 59, 0);
                // Adjust for the time zone offset
                var timezoneOffset = currentDate.getTimezoneOffset();
                currentDate.setMinutes(currentDate.getMinutes() - timezoneOffset);
                // Format the date to be compatible with the datetime-local input
                var formattedDate = currentDate.toISOString().slice(0, -8);
                document.getElementById("to_date").value = formattedDate;
            }
        },


        onclick_activity_details: function (ev) {
            ev.preventDefault();
            //get selected teams
            var x = document.getElementById("activity_team");
            var teams = [];
            for (var k = 0; k < x.children.length; k++) {
                var checkbox = x.children[k].querySelector("input[type=checkbox][name=team]");
                if (checkbox) {
                    if (checkbox.value === "all" && checkbox.checked) {
                        // If the "all" checkbox is checked, check all other checkboxes
                        var allCheckboxes = document.querySelectorAll("input[type=checkbox][name=team]:not([value='all'])");
                        for (var i = 0; i < allCheckboxes.length; i++) {
                            allCheckboxes[i].checked = true;
                            teams.push(allCheckboxes[i].value);
                        }
                    } else if (checkbox.checked) {
                        teams.push(checkbox.value);
                    }
                }
            }

            //get selected reps
            var x = document.getElementById("activity_rep");
            var reps = [];
            for (var k = 0; k < x.children.length; k++) {
                var checkbox = x.children[k].querySelector("input[type=checkbox][name=rep]");
                if (checkbox) {
                    if (checkbox.value === "all" && checkbox.checked) {
                        // If the "all" checkbox is checked, check all other checkboxes
                        var allCheckboxes = document.querySelectorAll("input[type=checkbox][name=rep]:not([value='all'])");
                        for (var i = 0; i < allCheckboxes.length; i++) {
                            allCheckboxes[i].checked = true;
                            reps.push(allCheckboxes[i].value);
                        }
                    } else if (checkbox.checked) {
                        reps.push(checkbox.value);
                    }
                }
            }

            //get selected meeting types
            var x = document.getElementById("activity_meeting_type");
            var meeting_types = [];
            for (var k = 0; k < x.children.length; k++) {
                var checkbox = x.children[k].querySelector("input[type=checkbox][name=meeting_type]");
                if (checkbox) {
                    if (checkbox.value === "all" && checkbox.checked) {
                        // If the "all" checkbox is checked, check all other checkboxes
                        var allCheckboxes = document.querySelectorAll("input[type=checkbox][name=meeting_type]:not([value='all'])");
                        for (var i = 0; i < allCheckboxes.length; i++) {
                            allCheckboxes[i].checked = true;
                            meeting_types.push(allCheckboxes[i].value);
                        }
                    } else if (checkbox.checked) {
                        meeting_types.push(checkbox.value);
                    }
                }
            }

            //get selected status
            var x = document.getElementById("activity_status");
            var status = [];
            for (var k = 0; k < x.children.length; k++) {
                var checkbox = x.children[k].querySelector("input[type=checkbox][name=status]");
                if (checkbox) {
                    if (checkbox.value === "all" && checkbox.checked) {
                        // If the "all" checkbox is checked, check all other checkboxes
                        var allCheckboxes = document.querySelectorAll("input[type=checkbox][name=status]:not([value='all'])");
                        for (var i = 0; i < allCheckboxes.length; i++) {
                            allCheckboxes[i].checked = true;
                            status.push(allCheckboxes[i].value);
                        }
                    } else if (checkbox.checked) {
                        status.push(checkbox.value);
                    }
                }
            }

            //get selected state of open/closed
            var x = document.getElementById("open_closed");
            var checkedValues = [];
            var checkboxes = x.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(function(checkbox) {
                if (checkbox.checked) {
                    checkedValues.push(checkbox.id);
                }
            });

            //get selected dates
            var from_date = document.getElementById("from_date").value;
            var to_date = document.getElementById("to_date").value;
            var dates = [from_date, to_date];

            rpc.query({
                        model: "calendar.event",
                        method: "get_activity_details_by_filter",
                        args: [teams, reps, meeting_types, checkedValues, status, dates],
                    }).then(function (result) {
                        $('#activity_details').empty();
                        var inner ='<table class="table table-sm table-sm">';
                        inner+= "<thread><tr style='background-color: silver;'><th><strong>Team</strong></th><th><strong>Rep</strong></th><th><strong>Company name</strong></th><th><strong>Contact</strong></th><th><strong>Customer type</strong></th><th><strong>Status</strong></th><th><strong>Meeting type</strong></th><th><strong>Activity quantity</strong></th><th><strong>Closed</strong></th></tr></thread>";
                        inner+='<tbody>';
                        for (var k = 0; k < result.length; k++) {
                            var team = result[k].team_name ? result[k].team_name : '';
                            var rep = result[k].rep ? result[k].rep : '';
                            var company = result[k].company_name ? result[k].company_name : '';
                            var contact = result[k].contact ? result[k].contact : '';
                            var meeting_type = result[k].meeting_type ? result[k].meeting_type : '';
                            var activity_quantity = result[k].activity_quantity ? result[k].activity_quantity : 0;
                            var customer_type = result[k].customer_type ? result[k].customer_type : '';
                            var status = result[k].status ? result[k].status : '';
                            if (result[k].completed == 'yes')
                                {
                                var completed = 'Yes'
                                    }
                            else
                                {
                                    var completed = 'No'
                                }
                           inner+= '<tr><td>'+team+'</td><td>'+rep+'</td><td>'+company+'</td><td>'+contact+'</td><td>'+customer_type+'</td><td>'+status+'</td><td>'+meeting_type+'</td><td>'+activity_quantity+'</td><td>'+completed+'</td></tr>';
                            }
                        inner+='</tbody>';
                        inner+='</table>';
                        $('#activity_details').append(inner);
                        })

        },


        renderElement: function (ev) {
            var self = this;
            $.when(this._super())
                .then(function (ev) {


                 rpc.query({
                        model: "calendar.event",
                        method: "get_activity_details",
                    }).then(function (result) {
                        var inner ='<table class="table table-sm table-sm">';
                        inner+= "<thread><tr style='background-color: silver;'><th><strong>Team</strong></th><th><strong>Rep</strong></th><th><strong>Company name</strong></th><th><strong>Contact</strong></th><th><strong>Customer type</strong></th><th><strong>Status</strong></th><th><strong>Meeting type</strong></th><th><strong>Activity quantity</strong></th><th><strong>Closed</strong></th></tr></thread>";
                        inner+='<tbody>';
                        for (var k = 0; k < result.length; k++) {
                            var team = result[k].team_name ? result[k].team_name : '';
                            var rep = result[k].rep ? result[k].rep : '';
                            var company = result[k].company_name ? result[k].company_name : '';
                            var contact = result[k].contact ? result[k].contact : '';
                            var meeting_type = result[k].meeting_type ? result[k].meeting_type : '';
                            var activity_quantity = result[k].activity_quantity ? result[k].activity_quantity : 0;
                            var customer_type = result[k].customer_type ? result[k].customer_type : '';
                            var status = result[k].status ? result[k].status : '';
                            if (result[k].completed == 'yes')
                                {
                                var completed = 'Yes'
                                    }
                            else
                                {
                                    var completed = 'No'
                                }
                           inner+= '<tr><td>'+team+'</td><td>'+rep+'</td><td>'+company+'</td><td>'+contact+'</td><td>'+customer_type+'</td><td>'+status+'</td><td>'+meeting_type+'</td><td>'+activity_quantity+'</td><td>'+completed+'</td></tr>';
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
                            checkbox.name = "team";
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
                                checkbox.name = "team";
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
                            checkbox.name = "rep";
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
                                checkbox.name = "rep";
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
                            checkbox.name = "meeting_type";
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
                                checkbox.name = "meeting_type";
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
                        method: "get_status",
                    })
                    .then(function (result) {
                        if (result[0]) {
                            var container = document.getElementById("activity_status");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "status";
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
                                checkbox.name = "status";
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