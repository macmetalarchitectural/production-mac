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
            'click #hoverDiv6': 'onclick_hoverDiv6',
            'change #activity_team': 'onclick_activity_details',
            'change #activity_rep': 'onclick_activity_details',
            'change #activity_meeting_type': 'onclick_activity_details',
            'change #open_closed': 'onclick_activity_details',
            'change #activity_status': 'onclick_activity_details',
            'click #from_date': 'onclick_from_date',
            'change #from_date': 'onclick_activity_details',
            'click #to_date': 'onclick_to_date',
            'change #to_date': 'onclick_activity_details',
            'change #activity_period': 'onclick_activity_details',
        },


        onclick_hoverDiv1: function (ev) {
            var hiddenDiv1 = $(ev.currentTarget).closest('.col-2').find("#hiddenDiv1");
            if (hiddenDiv1.is(":visible")) {
                hiddenDiv1.slideUp();
                $("#team_up").show();
                $("#team_down").hide();
            } else {
                hiddenDiv1.slideDown();
                $("#team_up").hide();
                $("#team_down").show();
            }
        },

        onclick_hoverDiv2: function (ev) {
            var hiddenDiv2 = $(ev.currentTarget).closest('.col-2').find("#hiddenDiv2");
            if (hiddenDiv2.is(":visible")) {
                hiddenDiv2.slideUp();
                $("#rep_up").show();
                $("#rep_down").hide();
            } else {
                hiddenDiv2.slideDown();
                $("#rep_up").hide();
                $("#rep_down").show();
            }
        },

        onclick_hoverDiv3: function (ev) {
            var hiddenDiv3 = $(ev.currentTarget).closest('.col-2').find("#hiddenDiv3");
            if (hiddenDiv3.is(":visible")) {
                hiddenDiv3.slideUp();
                $("#meeting_type_up").show();
                $("#meeting_type_down").hide();
            } else {
                hiddenDiv3.slideDown();
                $("#meeting_type_up").hide();
                $("#meeting_type_down").show();
            }
        },

        onclick_hoverDiv4: function (ev) {
            var hiddenDiv4 = $(ev.currentTarget).closest('.col-2').find("#hiddenDiv4");
            if (hiddenDiv4.is(":visible")) {
                hiddenDiv4.slideUp();
                $("#closed_up").show();
                $("#closed_down").hide();
            } else {
                hiddenDiv4.slideDown();
                $("#closed_up").hide();
                $("#closed_down").show();
            }
        },

        onclick_hoverDiv5: function (ev) {
            var hiddenDiv5 = $(ev.currentTarget).closest('.col-2').find("#hiddenDiv5");
            if (hiddenDiv5.is(":visible")) {
                hiddenDiv5.slideUp();
                $("#status_up").show();
                $("#status_down").hide();
            } else {
                hiddenDiv5.slideDown();
                $("#status_up").hide();
                $("#status_down").show();
            }
        },

        onclick_hoverDiv6: function (ev) {
            var hiddenDiv6 = $(ev.currentTarget).closest('.col-2').find("#hiddenDiv6");
            if (hiddenDiv6.is(":visible")) {
                hiddenDiv6.slideUp();
                $("#period_up").show();
                $("#period_down").hide();
            } else {
                hiddenDiv6.slideDown();
                $("#period_up").hide();
                $("#period_down").show();
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

        get_rep_by_team: function (ev, teams) {
            rpc.query({
                        model: "calendar.event",
                        method: "get_rep_by_team",
                        args: [teams],
                    })
                    .then(function (result) {
                        if (result[0]) {
                            var select_all= _t('Select all');
                            var container = document.getElementById("activity_rep");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "rep";
                            checkbox.value = "all";

                            // Create a label for the checkbox
                            var label = document.createElement("label");
                            label.appendChild(checkbox);
                            label.appendChild(document.createTextNode(select_all));

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
        },


        onclick_activity_details: function (ev) {
            ev.preventDefault();
            //get selected teams
            var activity_team = document.getElementById("activity_team");
            var teams = [];

            function toggleAllTeams(checked) {
                var allCheckboxes = document.querySelectorAll("input[type=checkbox][name=team]:not([value='all'])");
                for (var i = 0; i < allCheckboxes.length; i++) {
                    allCheckboxes[i].checked = checked;

                }
            }
            // Find the "all" checkbox element
            var allTeams = document.querySelector("input[type=checkbox][name=team][value='all']");
            // Attach event listener to the "all" checkbox
            allTeams.addEventListener("change", function() {
                toggleAllTeams(this.checked);
            });
            // Trigger the checked checkbox
            if (allTeams.checked) {
                toggleAllTeams(true);
            }
            else {
                for (var k = 0; k < activity_team.children.length; k++) {
                    var checkbox = activity_team.children[k].querySelector("input[type=checkbox][name=team]");
                    if (checkbox && checkbox.checked && checkbox.value !== "all") {
                        teams.push(checkbox.value);
                    }
                }
            }

            // If teams are selected, get reps for those teams
            if (teams.length != 0) {
                this.get_rep_by_team(ev, teams);
            }

            //get selected reps
            var activity_rep = document.getElementById("activity_rep");
            var reps = [];

            function toggleAllReps(checked) {
                var allCheckboxes = document.querySelectorAll("input[type=checkbox][name=rep]:not([value='all'])");
                for (var i = 0; i < allCheckboxes.length; i++) {
                    allCheckboxes[i].checked = checked;
                }
            }

             // Find the "all" checkbox element
            var allReps = document.querySelector("input[type=checkbox][name=rep][value='all']");
            // Attach event listener to the "all" checkbox
            allReps.addEventListener("change", function() {
                toggleAllReps(this.checked);
            });
            // Trigger the checked checkbox
            if (allReps.checked) {
                toggleAllReps(true);
            }
            else {
                for (var k = 0; k < activity_rep.children.length; k++) {
                    var checkbox = activity_rep.children[k].querySelector("input[type=checkbox][name=rep]");
                    if (checkbox && checkbox.checked && checkbox.value !== "all") {
                        reps.push(checkbox.value);
                    }
                }
            }

            //get selected meeting types
            var activity_meeting_type = document.getElementById("activity_meeting_type");
            var meeting_types = [];
            function toggleAllMeetingTypes(checked) {
                var allCheckboxes = document.querySelectorAll("input[type=checkbox][name=meeting_type]:not([value='all'])");
                for (var i = 0; i < allCheckboxes.length; i++) {
                    allCheckboxes[i].checked = checked;
                }
            }

            // Find the "all" checkbox element
            var allMeetingTypes = document.querySelector("input[type=checkbox][name=meeting_type][value='all']");
            // Attach event listener to the "all" checkbox
            allMeetingTypes.addEventListener("change", function() {
                toggleAllMeetingTypes(this.checked);
            });
            // Trigger the checked checkbox
            if (allMeetingTypes.checked) {
                toggleAllMeetingTypes(true);
            }
            else {
                for (var k = 0; k < activity_meeting_type.children.length; k++) {
                    var checkbox = activity_meeting_type.children[k].querySelector("input[type=checkbox][name=meeting_type]");
                    if (checkbox && checkbox.checked && checkbox.value !== "all") {
                        meeting_types.push(checkbox.value);
                    }
                }
            }

            //get selected status
            var activity_status = document.getElementById("activity_status");
            var status = [];
            function toggleAllStatus(checked) {
                var allCheckboxes = document.querySelectorAll("input[type=checkbox][name=status]:not([value='all'])");
                for (var i = 0; i < allCheckboxes.length; i++) {
                    allCheckboxes[i].checked = checked;
                }
            }

             // Find the "all" checkbox element
            var allStatus = document.querySelector("input[type=checkbox][name=status][value='all']");
            // Attach event listener to the "all" checkbox
            allStatus.addEventListener("change", function() {
                toggleAllStatus(this.checked);
            });
            // Trigger the checked checkbox
            if (allStatus.checked) {
                toggleAllStatus(true);
            }
            else {
                for (var k = 0; k < activity_status.children.length; k++) {
                    var checkbox = activity_status.children[k].querySelector("input[type=checkbox][name=status]");
                    if (checkbox && checkbox.checked && checkbox.value !== "all") {
                        status.push(checkbox.value);
                    }
                }
            }

            //get selected state of open/closed
            var open_closed = document.getElementById("open_closed");
            var completed = [];
            function toggleAllCompleted(checked) {
                var allCheckboxes = document.querySelectorAll("input[type='checkbox'][name=completed]:not([id='all'])");
                for (var i = 0; i < allCheckboxes.length; i++) {
                    allCheckboxes[i].checked = checked;
                }
            }

            // Find the "all" checkbox element
            var allCompleted = document.querySelector("input[type=checkbox][name=completed][id='all']");
            // Attach event listener to the "all" checkbox
            allCompleted.addEventListener("change", function() {
                toggleAllCompleted(this.checked);
            });
            // Trigger the checked checkbox
            if (allCompleted.checked) {
                toggleAllCompleted(true);
            }
            else {
                for (var k = 0; k < open_closed.children.length; k++) {
                    var checkbox = open_closed.children[k].querySelector("input[type=checkbox][name=completed]");
                    if (checkbox && checkbox.checked) {
                        completed.push(checkbox.id);
                    }
                }
            }

            //get selected period
            var activity_period = document.getElementById("activity_period").value;

            //get selected dates
            var from_date = document.getElementById("from_date").value;
            var to_date = document.getElementById("to_date").value;
            var dates = [from_date, to_date];

            rpc.query({
                        model: "calendar.event",
                        method: "get_activity_details_by_filter",
                        args: [teams, reps, meeting_types, completed, status, dates, activity_period],
                    }).then(function (result) {
                        $('#activity_details').empty();
                        var inner ='<table class="table table-sm table-sm">';
                        var team =  _t('Team');
                        var rep =  _t('Rep');
                        var company =  _t('Company name');
                        var contact =  _t('Contact');
                        var customer_type =  _t('Customer type');
                        var status =  _t('Status');
                        var meeting_type =  _t('Meeting type');
                        var activity_quantity =  _t('Activity quantity');
                        var closed =  _t('Closed');
                        var inner = '<table class="table table-sm table-sm">';
                        inner += "<thread><tr style='background-color: silver;'><th><strong>" + team + "</strong></th><th><strong>" + rep + "</strong></th><th><strong>" + company + "</strong></th><th><strong>" + contact + "</strong></th><th><strong>" + customer_type + "</strong></th><th><strong>" + status + "</strong></th><th><strong>" + meeting_type + "</strong></th><th><strong>" + activity_quantity + "</strong></th><th><strong>" + closed + "</strong></th></tr></thread>";
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
                                var completed = _t('Yes');
                                    }
                            else
                                {
                                    var completed = _t('No');
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
                        var team =  _t('Team');
                        var rep =  _t('Rep');
                        var company =  _t('Company name');
                        var contact =  _t('Contact');
                        var customer_type =  _t('Customer type');
                        var status =  _t('Status');
                        var meeting_type =  _t('Meeting type');
                        var activity_quantity =  _t('Activity quantity');
                        var closed =  _t('Closed');
                        var inner = '<table class="table table-sm table-sm">';
                        inner += "<thread><tr style='background-color: silver;'><th><strong>" + team + "</strong></th><th><strong>" + rep + "</strong></th><th><strong>" + company + "</strong></th><th><strong>" + contact + "</strong></th><th><strong>" + customer_type + "</strong></th><th><strong>" + status + "</strong></th><th><strong>" + meeting_type + "</strong></th><th><strong>" + activity_quantity + "</strong></th><th><strong>" + closed + "</strong></th></tr></thread>";
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
                                var completed = _t('Yes');
                                    }
                            else
                                {
                                    var completed = _t('No');
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
                            var select_all= _t('Select all');
                            var container = document.getElementById("activity_team");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "team";
                            checkbox.value = "all";

                            // Create a label for the checkbox
                            var label = document.createElement("label");
                            label.appendChild(checkbox);
                            label.appendChild(document.createTextNode(select_all));

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
                            var select_all= _t('Select all');
                            var container = document.getElementById("activity_rep");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "rep";
                            checkbox.value = "all";

                            // Create a label for the checkbox
                            var label = document.createElement("label");
                            label.appendChild(checkbox);
                            label.appendChild(document.createTextNode(select_all));

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
                            var select_all= _t('Select all');
                            var container = document.getElementById("activity_meeting_type");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "meeting_type";
                            checkbox.value = "all";

                            // Create a label for the checkbox
                            var label = document.createElement("label");
                            label.appendChild(checkbox);
                            label.appendChild(document.createTextNode(select_all));

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
                            var select_all= _t('Select all');
                            var container = document.getElementById("activity_status");
                            container.innerHTML = ""; // Clear any previous content
                            var checkbox = document.createElement("input");
                            checkbox.type = "checkbox";
                            checkbox.name = "status";
                            checkbox.value = "all";

                            // Create a label for the checkbox
                            var label = document.createElement("label");
                            label.appendChild(checkbox);
                            label.appendChild(document.createTextNode(select_all));

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


            rpc.query({
                        model: "calendar.event",
                        method: "get_period",
                    })
                        .then(function (result) {

                                if(result[0]){
                                  var selectElem = document.getElementById("activity_period");
                                  $(selectElem).empty();
                                  for (var k = 0; k < result.length; k++) {
                                  var item =result[k].name;
                                  var value =result[k].id;
                                  var element = document.createElement("option");
                                  element.innerText = item;
                                  element.value = value;
                                  selectElem.append(element);
                                    }
                                }
                                })



           });
        },
    });
    core.action_registry.add('activity_dashboard', ActionMenu);

});