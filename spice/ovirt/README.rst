Selenium tests were inspired by rhevm-raut. Raut is written by Pavel Novotny
<pnovotny@redhat.com>

    * https://code.engineering.redhat.com/gerrit/#/admin/projects/rhevm-raut
    * https://mojo.redhat.com/docs/DOC-1084114
    * http://art-build-srv.qa.lab.tlv.redhat.com/pytest/rhel/7.2/Packages/
    * http://git.app.eng.bos.redhat.com/git/rhevm-qe-utils.git
    * http://art-build-srv.qa.lab.tlv.redhat.com/help/
    * https://code.engineering.redhat.com/gerrit/gitweb?p=rhevm-qe-automation/rhevm-art.git;a=tree

Explanations "page model" conception.
-------------------------------------

Sometimes you can see next code:

    _model = VMPopupModel

    ...

    def init_validation(self):
        self._model.name

It is very tricky code.

Here self._model.name is a "property". See at elements.py:

    class RootPageElement(property):
    ...

See also:

    * https://docs.python.org/2/howto/descriptor.html
    * http://stackoverflow.com/questions/136097

Examples:

    vms_base.GuestAgentIsNotResponsiveDlgModel(tab_controller.driver).ok_btn

    vms_base.GuestAgentIsNotResponsiveDlgModel.ok_btn._by
    Out[44]: 'id'

    vms_base.GuestAgentIsNotResponsiveDlgModel.ok_btn._locator
    Out[45]: 'DefaultConfirmationPopupView_SpiceWithoutAgentOK'


