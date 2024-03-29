#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `{{ cookiecutter.project_slug }}` package."""

import os
import json
import unittest
import shutil
import tempfile
import io
import uuid
import re
from werkzeug.datastructures import FileStorage
import {{ cookiecutter.project_slug }}
from {{ cookiecutter.project_slug }} import ErrorResponse


class Test{{ cookiecutter.service_name.capitalize() }}(unittest.TestCase):
    """Tests for `{{ cookiecutter.project_slug }}` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self._temp_dir = tempfile.mkdtemp()
        {{ cookiecutter.project_slug }}.app.testing = True
        {{ cookiecutter.project_slug }}.app.config[{{ cookiecutter.project_slug }}.JOB_PATH_KEY] = self._temp_dir
        {{ cookiecutter.project_slug }}.app.config[{{ cookiecutter.project_slug }}.WAIT_COUNT_KEY] = 1
        {{ cookiecutter.project_slug }}.app.config[{{ cookiecutter.project_slug }}.SLEEP_TIME_KEY] = 0
        self._app = {{ cookiecutter.project_slug }}.app.test_client()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        shutil.rmtree(self._temp_dir)

    def test_error_response(self):
        er = ErrorResponse()
        self.assertEqual(er.errorCode, '')
        self.assertEqual(er.message, '')
        self.assertEqual(er.description, '')
        self.assertEqual(er.stackTrace, '')
        self.assertEqual(er.threadId, '')
        self.assertTrue(er.timeStamp is not None)

    def test_get_submit_dir(self):
        spath = os.path.join(self._temp_dir, {{ cookiecutter.project_slug }}.SUBMITTED_STATUS)
        self.assertEqual({{ cookiecutter.project_slug }}.get_submit_dir(), spath)

    def test_get_processing_dir(self):
        spath = os.path.join(self._temp_dir, {{ cookiecutter.project_slug }}.PROCESSING_STATUS)
        self.assertEqual({{ cookiecutter.project_slug }}.get_processing_dir(), spath)

    def test_get_done_dir(self):
        spath = os.path.join(self._temp_dir, {{ cookiecutter.project_slug }}.DONE_STATUS)
        self.assertEqual({{ cookiecutter.project_slug }}.get_done_dir(), spath)

    def test_create_task_success(self):
        pdict = {}
        pdict['remoteip'] = '1.2.3.4'
        pdict[{{ cookiecutter.project_slug }}.ALPHA_PARAM] = 0.01
        pdict[{{ cookiecutter.project_slug }}.BETA_PARAM] = 0.5
        intfile = FileStorage(stream=io.BytesIO(b'hi there'),
                              filename='yo.txt')
        pdict[{{ cookiecutter.project_slug }}.INTERACTION_FILE_PARAM] = intfile
        res = {{ cookiecutter.project_slug }}.create_task(pdict)
        self.assertTrue(res is not None)

        snp_path = os.path.join({{ cookiecutter.project_slug }}.get_submit_dir(),
                                pdict['remoteip'], res,
                                {{ cookiecutter.project_slug }}.INTERACTION_FILE_PARAM)
        self.assertTrue(os.path.isfile(snp_path))

    def test_create_task_submitdir_is_a_file(self):
        open({{ cookiecutter.project_slug }}.get_submit_dir(), 'a').close()
        pdict = {}
        pdict['remoteip'] = '1.2.3.4'
        pdict[{{ cookiecutter.project_slug }}.ALPHA_PARAM] = 0.01
        pdict[{{ cookiecutter.project_slug }}.BETA_PARAM] = 0.5
        intfile = FileStorage(stream=io.BytesIO(b'hi there'),
                              filename='yo.txt')
        pdict[{{ cookiecutter.project_slug }}.INTERACTION_FILE_PARAM] = intfile
        try:
            {{ cookiecutter.project_slug }}.create_task(pdict)
            self.fail('Expected NotADirectoryError')
        except NotADirectoryError:
            pass

    def test_get_task_basedir_none(self):
        self.assertEqual({{ cookiecutter.project_slug }}.get_task('foo'), None)
        
    def test_get_task_basedir_not_a_directory(self):
        somefile = os.path.join(self._temp_dir, 'hi')
        open(somefile, 'a').close()
        self.assertEqual({{ cookiecutter.project_slug }}.get_task('foo', basedir=somefile), None)

    def test_get_task_for_none_uuid(self):
        self.assertEqual({{ cookiecutter.project_slug }}.get_task(None,
                                              basedir=self._temp_dir), None)

    def test_get_task_for_nonexistantuuid(self):
        self.assertEqual({{ cookiecutter.project_slug }}.get_task(str(uuid.uuid4()),
                                              basedir=self._temp_dir), None)

    def test_get_task_for_validuuid(self):
        somefile = os.path.join(self._temp_dir, '1')
        open(somefile, 'a').close()
        theuuid_dir = os.path.join(self._temp_dir, '1.2.3.4', '1234')
        os.makedirs(theuuid_dir, mode=0o755)

        someipfile = os.path.join(self._temp_dir, '1.2.3.4', '1')
        open(someipfile, 'a').close()
        self.assertEqual({{ cookiecutter.project_slug }}.get_task('1234',
                                              basedir=self._temp_dir),
                         theuuid_dir)

    def test_wait_for_task_uuid_none(self):
        self.assertEqual({{ cookiecutter.project_slug }}.wait_for_task(None), None)

    def test_wait_for_task_uuid_not_found(self):
        self.assertEqual({{ cookiecutter.project_slug }}.wait_for_task('foo'), None)

    def test_wait_for_task_uuid_found(self):
        taskdir = os.path.join(self._temp_dir, 'done', '1.2.3.4', 'haha')
        os.makedirs(taskdir, mode=0o755)
        self.assertEqual({{ cookiecutter.project_slug }}.wait_for_task('haha'), taskdir)

    def test_baseurl(self):
        """Test something."""
        rv = self._app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('{{ cookiecutter.project_name }}' in str(rv.data))

    def test_delete(self):
        rv = self._app.delete({{ cookiecutter.project_slug }}.SERVICE_NS +
                              '/hehex')

        self.assertEqual(rv.status_code, 200)
        hehefile = os.path.join(self._temp_dir,
                                {{ cookiecutter.project_slug }}.DELETE_REQUESTS,
                                'hehex')
        self.assertTrue(os.path.isfile(hehefile))

        # try with not set path
        rv = self._app.delete({{ cookiecutter.project_slug }}.SERVICE_NS)
        self.assertEqual(rv.status_code, 405)

        # try with path greater then 40 characters
        rv = self._app.delete({{ cookiecutter.project_slug }}.SERVICE_NS +
                              '/' + 'a' * 41)
        self.assertEqual(rv.status_code, 400)

        # try where we get os error
        xdir = os.path.join(self._temp_dir,
                            {{ cookiecutter.project_slug }}.DELETE_REQUESTS,
                            'hehe')
        os.makedirs(xdir, mode=0o755)
        rv = self._app.delete({{ cookiecutter.project_slug }}.SERVICE_NS +
                              '/hehe')
        self.assertEqual(rv.status_code, 500)
        
    def test_post_missing_required_parameter(self):
        pdict = {}
        pdict[{{ cookiecutter.project_slug }}.ALPHA_PARAM] = 0.4,
        rv = self._app.post({{ cookiecutter.project_slug }}.SERVICE_NS +
                            '/', data=pdict,
                            follow_redirects=True)
        self.assertTrue('interactionfile' in rv.json['errors'])

        self.assertEqual(rv.status_code, 400)

    def test_post_create_task_fails(self):
        open({{ cookiecutter.project_slug }}.get_submit_dir(), 'a').close()
        pdict = {}
        pdict[{{ cookiecutter.project_slug }}.ALPHA_PARAM] = 0.5
        pdict[{{ cookiecutter.project_slug }}.BETA_PARAM] = 1.0
        pdict[{{ cookiecutter.project_slug }}.INTERACTION_FILE_PARAM] = (io.BytesIO(b'hi there'),
                                                      'yo.txt')
        rv = self._app.post({{ cookiecutter.project_slug }}.SERVICE_NS,
                            data=pdict,
                            follow_redirects=True)
        self.assertEqual(rv.status_code, 500)
        self.assertTrue('Error' in rv.json['message'])

    def test_post_ndex(self):
        pdict = {}
        pdict[{{ cookiecutter.project_slug }}.ALPHA_PARAM] = 0.5
        pdict[{{ cookiecutter.project_slug }}.BETA_PARAM] = 1.0
        pdict[{{ cookiecutter.project_slug }}.INTERACTION_FILE_PARAM] = (io.BytesIO(b'hi there'),
                                                      'yo.txt')
        rv = self._app.post({{ cookiecutter.project_slug }}.SERVICE_NS,
                            data=pdict,
                            follow_redirects=True)
        self.assertEqual(rv.status_code, 202)
        res = rv.headers['Location']
        self.assertTrue(res is not None)
        self.assertTrue({{ cookiecutter.project_slug }}.SERVICE_NS in res)

        uuidstr = re.sub('^.*/', '', res)
        {{ cookiecutter.project_slug }}.app.config[{{ cookiecutter.project_slug }}.JOB_PATH_KEY] = self._temp_dir

        tpath = {{ cookiecutter.project_slug }}.get_task(uuidstr,
                                     basedir={{ cookiecutter.project_slug }}.get_submit_dir())
        self.assertTrue(os.path.isdir(tpath))
        jsonfile = os.path.join(tpath, {{ cookiecutter.project_slug }}.TASK_JSON)
        ifile = os.path.join(tpath, {{ cookiecutter.project_slug }}.INTERACTION_FILE_PARAM)
        self.assertTrue(os.path.isfile(ifile))
        self.assertTrue(os.path.isfile(jsonfile))
        with open(jsonfile, 'r') as f:
            jdata = json.load(f)

        self.assertEqual(jdata['tasktype'], 'ddot_ontology')
        self.assertEqual(jdata[{{ cookiecutter.project_slug }}.ALPHA_PARAM], 0.5)
        self.assertEqual(jdata[{{ cookiecutter.project_slug }}.BETA_PARAM], 1.0)

    def test_get_status_no_submidir(self):
        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS + '/status')
        data = json.loads(rv.data)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['restVersion'],
                         {{ cookiecutter.project_slug }}.__version__)
        self.assertEqual(len(data['load']), 3)
        self.assertTrue(data['pcDiskFull'], -1)
        self.assertEqual(rv.status_code, 200)

    def test_get_status(self):
        submitdir = {{ cookiecutter.project_slug }}.get_submit_dir()
        os.makedirs(submitdir, mode=0o755)
        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS + '/status')
        data = json.loads(rv.data)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['restVersion'],
                         {{ cookiecutter.project_slug }}.__version__)
        self.assertEqual(len(data['load']), 3)
        self.assertTrue(data['pcDiskFull'] is not None)
        self.assertEqual(rv.status_code, 200)
        
    def test_get_id_none(self):
        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS)
        self.assertEqual(rv.status_code, 405)

    def test_get_id_not_found(self):
        done_dir = os.path.join(self._temp_dir,
                                {{ cookiecutter.project_slug }}.DONE_STATUS)
        os.makedirs(done_dir, mode=0o755)
        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS +
                           '/1234')
        data = json.loads(rv.data)
        self.assertEqual(data[{{ cookiecutter.project_slug }}.STATUS_RESULT_KEY],
                         {{ cookiecutter.project_slug }}.NOTFOUND_STATUS)
        self.assertEqual(rv.status_code, 410)

    def test_get_id_found_in_submitted_status(self):
        task_dir = os.path.join(self._temp_dir,
                                {{ cookiecutter.project_slug }}.SUBMITTED_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS +
                           '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[{{ cookiecutter.project_slug }}.STATUS_RESULT_KEY],
                         {{ cookiecutter.project_slug }}.SUBMITTED_STATUS)
        self.assertEqual(rv.status_code, 200)

    def test_get_id_found_in_processing_status(self):
        task_dir = os.path.join(self._temp_dir,
                                {{ cookiecutter.project_slug }}.PROCESSING_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS +
                           '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[{{ cookiecutter.project_slug }}.STATUS_RESULT_KEY],
                         {{ cookiecutter.project_slug }}.PROCESSING_STATUS)
        self.assertEqual(rv.status_code, 200)

    def test_get_id_found_in_done_status_no_result_file(self):
        task_dir = os.path.join(self._temp_dir,
                                {{ cookiecutter.project_slug }}.DONE_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS +
                           '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data['message'],
                         'No result found')
        self.assertEqual(rv.status_code, 500)

    def test_get_id_found_in_done_status_with_result_file_no_task_file(self):
        task_dir = os.path.join(self._temp_dir,
                                {{ cookiecutter.project_slug }}.DONE_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        resfile = os.path.join(task_dir, {{ cookiecutter.project_slug }}.RESULT)
        with open(resfile, 'w') as f:
            f.write('{ "hello": "there"}')
            f.flush()

        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS +
                           '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[{{ cookiecutter.project_slug }}.STATUS_RESULT_KEY],
                         {{ cookiecutter.project_slug }}.DONE_STATUS)
        self.assertEqual(data[{{ cookiecutter.project_slug }}.RESULT_KEY]['hello'], 'there')
        self.assertEqual(rv.status_code, 200)

    def test_get_id_found_in_done_status_with_result_file_with_task_file(self):
        task_dir = os.path.join(self._temp_dir,
                                {{ cookiecutter.project_slug }}.DONE_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        resfile = os.path.join(task_dir, {{ cookiecutter.project_slug }}.RESULT)
        with open(resfile, 'w') as f:
            f.write('{ "hello": "there"}')
            f.flush()
        tfile = os.path.join(task_dir, {{ cookiecutter.project_slug }}.TASK_JSON)
        with open(tfile, 'w') as f:
            f.write('{"task": "yo"}')
            f.flush()

        rv = self._app.get({{ cookiecutter.project_slug }}.SERVICE_NS +
                           '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[{{ cookiecutter.project_slug }}.STATUS_RESULT_KEY],
                         {{ cookiecutter.project_slug }}.DONE_STATUS)
        self.assertEqual(data[{{ cookiecutter.project_slug }}.RESULT_KEY]['hello'], 'there')
        self.assertEqual(rv.status_code, 200)

    def test_log_task_json_file_with_none(self):
        self.assertEqual({{ cookiecutter.project_slug }}.log_task_json_file(None), None)
