# Copyright 2015 Openstack Foundation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import xml.etree.ElementTree as XML
import jenkins_jobs.modules.base

"""
The view list module handles creating Jenkins List views.

To create a list view specify ``list`` in the ``view-type`` attribute
to the :ref:`View-list` definition.

:View Parameters:
    * **name** (`str`): The name of the view.
    * **view-type** (`str`): The type of view.
    * **description** (`str`): A description of the view. (optional)
    * **filter-executors** (`bool`): Show only executors that can
      execute the included views. (default false)
    * **filter-queue** (`bool`): Show only included jobs in builder
      queue. (default false)
    * **job-name** (`list`): List of jobs to be included.
    * **job-filters** (`dict`): Job filters to be included. Requires
      :jenkins-wiki:`View Job Filters <View+Job+Filters>`

        * **most-recent** (`dict`)
            :most-recent: * **max-to-include** (`int`): Maximum number of jobs
                            to include. (default 0)
                          * **check-start-time** (`bool`): Check job start
                            time. (default false)

        * **build-duration** (`dict`)
            :build-duration: * **match-type** ('str'): Jobs that match a filter
                               to include. (default includeMatched)
                             * **build-duration-type** ('str'): Duration of the
                               build. (default Latest)
                             * **amount-type**: ('str'): Duration in hours,
                               days or builds. (default Hours)
                             * **amount**: ('int'): How far back to check.
                               (default 0)
                             * **less-than**: ('bool'): Check build duration
                               less than or more than. (default True)
                             * **build-duration-minutes**: ('int'): Build
                               duration minutes. (default 0)

        * **build-trend** (`dict`)
            :build-trend: * **match-type** ('str'): Jobs that match a filter
                               to include. (default includeMatched)
                             * **build-trend-type** ('str'): Duration of the
                               build. (default Latest)
                             * **amount-type**: ('str'): Duration in hours,
                               days or builds. (default Hours)
                             * **amount**: ('int'): How far back to check.
                               (default 0)
                             * **status**: ('str'): Job status.
                               (default Completed)

        * **job-status** (`dict`)
            :job-status: * **match-type** ('str'): Jobs that match a filter
                               to include. (default includeMatched)
                             * **unstable** ('bool'): Jobs with status
                               unstable. (default False)
                             * **failed** ('bool'): Jobs with status
                               failed. (default False)
                             * **aborted** ('bool'): Jobs with status
                               aborted. (default False)
                             * **disabled** ('bool'): Jobs with status
                               disabled. (default False)
                             * **stable** ('bool'): Jobs with status
                               stable. (default False)

    * **columns** (`list`): List of columns to be shown in view.
    * **regex** (`str`): . Regular expression for selecting jobs
      (optional)
    * **recurse** (`bool`): Recurse in subfolders.(default false)
    * **status-filter** (`bool`): Filter job list by enabled/disabled
      status. (optional)
"""

COLUMN_DICT = {
    'status': 'hudson.views.StatusColumn',
    'weather': 'hudson.views.WeatherColumn',
    'job': 'hudson.views.JobColumn',
    'last-success': 'hudson.views.LastSuccessColumn',
    'last-failure': 'hudson.views.LastFailureColumn',
    'last-duration': 'hudson.views.LastDurationColumn',
    'build-button': 'hudson.views.BuildButtonColumn',
    'last-stable': 'hudson.views.LastStableColumn',
}


class List(jenkins_jobs.modules.base.Base):
    sequence = 0

    def root_xml(self, data):
        root = XML.Element('hudson.model.ListView')
        XML.SubElement(root, 'name').text = data['name']
        desc_text = data.get('description', None)
        if desc_text is not None:
            XML.SubElement(root, 'description').text = desc_text

        filterExecutors = data.get('filter-executors', False)
        FE_element = XML.SubElement(root, 'filterExecutors')
        FE_element.text = 'true' if filterExecutors else 'false'

        filterQueue = data.get('filter-queue', False)
        FQ_element = XML.SubElement(root, 'filterQueue')
        FQ_element.text = 'true' if filterQueue else 'false'

        XML.SubElement(root, 'properties',
                       {'class': 'hudson.model.View$PropertyList'})

        jn_xml = XML.SubElement(root, 'jobNames')
        jobnames = data.get('job-name', None)
        XML.SubElement(jn_xml, 'comparator', {'class':
                       'hudson.util.CaseInsensitiveComparator'})
        if jobnames is not None:
            for jobname in jobnames:
                XML.SubElement(jn_xml, 'string').text = str(jobname)

        job_filter_xml = XML.SubElement(root, 'jobFilters')
        jobfilters = data.get('job-filters', [])

        for jobfilter in jobfilters:
            if jobfilter == 'most-recent':
                mr_xml = XML.SubElement(job_filter_xml,
                                        'hudson.views.MostRecentJobsFilter')
                mr_xml.set('plugin', 'view-job-filters')
                mr_data = jobfilters.get('most-recent')
                mapping = [
                    ('max-to-include', 'maxToInclude', '0'),
                    ('check-start-time', 'checkStartTime', False),
                ]
                convert_mapping_to_xml(mr_xml, mr_data, mapping,
                                       fail_required=True)

            if jobfilter == 'build-duration':
                bd_xml = XML.SubElement(job_filter_xml,
                                        'hudson.views.BuildDurationFilter')
                bd_xml.set('plugin', 'view-job-filters')
                bd_data = jobfilters.get('build-duration')
                mapping = [
                    ('match-type', 'includeExcludeTypeString',
                        'includeMatched'),
                    ('build-duration-type', 'buildCountTypeString', 'Latest'),
                    ('amount-type', 'amountTypeString', 'Hours'),
                    ('amount', 'amount', '0'),
                    ('less-than', 'lessThan', True),
                    ('build-duration-minutes', 'buildDurationMinutes', '0'),
                ]
                convert_mapping_to_xml(bd_xml, bd_data, mapping,
                                       fail_required=True)

            if jobfilter == 'build-trend':
                bt_xml = XML.SubElement(job_filter_xml,
                                        'hudson.views.BuildTrendFilter')
                bt_xml.set('plugin', 'view-job-filters')
                bt_data = jobfilters.get('build-trend')
                mapping = [
                    ('match-type', 'includeExcludeTypeString',
                        'includeMatched'),
                    ('build-trend-type', 'buildCountTypeString', 'Latest'),
                    ('amount-type', 'amountTypeString', 'Hours'),
                    ('amount', 'amount', '0'),
                    ('status', 'statusTypeString', 'Completed'),
                ]
                convert_mapping_to_xml(bt_xml, bt_data, mapping,
                                       fail_required=True)

            if jobfilter == 'job-status':
                js_xml = XML.SubElement(job_filter_xml,
                                        'hudson.views.JobStatusFilter')
                js_xml.set('plugin', 'view-job-filters')
                js_data = jobfilters.get('job-status')
                mapping = [
                    ('match-type', 'includeExcludeTypeString',
                        'includeMatched'),
                    ('unstable', 'unstable', False),
                    ('failed', 'failed', False),
                    ('aborted', 'aborted', False),
                    ('disabled', 'disabled', False),
                    ('stable', 'stable', False),
                ]
                convert_mapping_to_xml(js_xml, js_data, mapping,
                                       fail_required=True)

        c_xml = XML.SubElement(root, 'columns')
        columns = data.get('columns', [])
        for column in columns:
            if column in COLUMN_DICT:
                XML.SubElement(c_xml, COLUMN_DICT[column])

        regex = data.get('regex', None)
        if regex is not None:
            XML.SubElement(root, 'includeRegex').text = regex

        recurse = data.get('recurse', False)
        R_element = XML.SubElement(root, 'recurse')
        R_element.text = 'true' if recurse else 'false'

        statusfilter = data.get('status-filter', None)
        if statusfilter is not None:
            SF_element = XML.SubElement(root, 'statusFilter')
            SF_element.text = 'true' if statusfilter else 'false'

        return root
