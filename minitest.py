#!/usr/bin/env python

# Copyleft (c) 2016 Cocobug All Rights Reserved.

from blessings import Terminal
import types,string

__all__ =["testGroup","testUnit"]

SUCESS_STATUS=1
FAILURE_STATUS=2
WARNING_STATUS=4
CRITICAL_STATUS=8

class testCoreOutOfTests(IndexError):
    pass

class testGroup(object):
    """TestGroup, group a number of testUnit, exec them and print the results"""
    def __init__(self,name="",terminal=None,prefix="",verbose=False,align=0):
        self._tests=[]
        self.name=name
        self.t=terminal
        self.prefix=prefix
        if self.t==None:
            self.t=Terminal()
        self.results=[]
        self.sucess_text= self.t.green("sucess")
        self.failure_text=self.t.bright_red("failure")
        self.warning_text=self.t.bright_yellow("warning")
        self.critical_text=self.t.bold_bright_red("critical")
        self.verbose=verbose
        self.align=align


    def addTest(self,testUnit):
        self._tests.append(testUnit)

    def test(self):
        "Execute all tests, some options might exist at some point"
        module_sucess,module_total=0,0

        print(self.prefix+"+ Executing test group "+self.pretty_group(self.name))
        oldprefix=self.prefix
        self.prefix+="|  "
        self.results=[]

        for test in self._tests:
            try:
                sucess,total,failures=self.print_result(test.test())
            except:
                sucess,total,failures=self.print_result([])

            print(self.pretty_subtests(test.name,sucess,total))

            if sucess==total:
                module_sucess+=1
            module_total+=1
            for failure in failures:
                print(failure)
            self.results.append([self,SUCESS_STATUS,""])
        self.prefix=oldprefix

        print(self.pretty_group_result(module_sucess,module_total))
        return self.results

    def print_result(self,table):
        "Get the array of sucess/failures and print according to the options (still none yet)"
        total=len(table)
        sucess=0
        results_array=[]
        nb=0

        for item,status,infos in table:
            nb+=1
            if status:
                sucess+=1
            if self.verbose or not status:
                results_array.append(self.pretty_result(status,nb,item,infos))
        return sucess,total,results_array


    def pretty_group_result(self,module_sucess,module_total):
        "Prettyfying the result of the batch of tests"
        bloc=self.prefix+"+ Done "
        return bloc+self.pretty_group(self.name)+self.pretty_dots(bloc,len(self.name))+self.pretty_succesrate(module_sucess,module_total)

    def pretty_name(self,item):
        "Just a pretty way of showing the name of a test"
        try:
            return item.__name__.strip("<>")
        except:
            return str(item)

    def pretty_subtests(self,name,sucess,total):
        "Pretty way of showing the result of the group of tests"
        bloc=self.prefix+"testing "+ self.pretty_test(name)
        return bloc+self.pretty_dots(bloc)+self.pretty_succesrate(sucess,total)

    def pretty_result(self,status,nb,item,infos):
        "Just a pretty way of showing the result of one test"
        bloc=self.prefix+" * "+" ["+str(nb)+"] "+self.pretty_name(item)
        return bloc+self.pretty_dots(bloc)+self.pretty_status(status)+self.pretty_info(infos)

    def pretty_dots(self,bloc,padding=0):
        lenbloc=len(bloc)+padding
        if (self.align>lenbloc+2):
            dots="."*(self.align-lenbloc)
        else:
            dots=".."
        return dots

    def pretty_info(self,infos):
        "Prettyfy the additional infos"
        if infos=="":
            return ""
        return self.t.italic(" ("+str(infos)+")")

    def pretty_status(self,status):
        "Prettyfy the status of the test"
        if status==SUCESS_STATUS:
            return self.sucess_text
        elif status==FAILURE_STATUS:
            return self.failure_text
        elif status==WARNING_STATUS:
            return self.warning_text
        else:
            return self.critical_text

    def pretty_group(self,name):
        "Prettify the name of the testGroup"
        return self.t.bold(name)

    def pretty_test(self,test):
        "Prettify the name of the testUnit"
        return test

    def pretty_succesrate(self,sucess,total):
        if sucess==total:
            wrap=self.t.green
            txt=self.sucess_text
        else:
            wrap=self.t.bright_red
            txt=self.failure_text
        return wrap(txt+" ["+str(sucess)+"/"+str(total)+"]")

    def __str__(self):
        return self.name

class testUnit(object):
    """A very basic test unit, only test() is mandatory
        test(): should return a list of [function,status,infos]
        Function added as test should raise error if incorect (assert is your friend),
            you can customise the test unit in any way that the field info become actually informative
        The whole class can (should) be modified to hold the test environement
        """
    def __init__(self,name):
        "The name if the name of the group of test executed"
        self._tests=[]
        self.name=name
        self.results=[]

    def addTest(self,test):
        "Add a function to the test unit"
        self._tests.append(test)

    def test(self):
        "Execute all tests"
        self.results=[]
        for test in self._tests:
            try:
                test()
                self.addResult(test,SUCESS_STATUS,'')
            except Exception as e:
                self.addResult(test,FAILURE_STATUS,e)
        return self.results

    def addResult(self,testName,status,info):
        self.results.append([testName,status,info])

class simpleTestUnit(testUnit):
    """Very simple test function, it tries to autodetect tests and add them and batch test them,
    this is not default behavior and should not be expected from other functions
    The very usage of this self.list_ongoing_tests makes the class non embetted effect protected and non-thread-friendly
    Note that using list_ongoing_tests and addResult together can lead to unpredictable results, use addSucess and addFailure instead"""

    def __init__(self,name):
        super(simpleTestUnit, self).__init__(name)
        self.results=[]
        self.list_ongoing_tests=[]
        self.userTests=[]
        self._simpleTestList=[]

    def currentTest(self,name=None):
        "Get the current test"
        if name==None:
            try:
                return self.list_ongoing_tests.pop()
            except IndexError:
                raise testCoreOutOfTests
        else:
            return self.list_ongoing_tests.append(name)


    def addSucess(self):
        "Mark the sucess of the current test (named in the function by self.currentTest)"
        self.addResult(self.currentTest(),SUCESS_STATUS,"")

    def addFailure(self,msg):
        "Mark the failure of the current test"
        self.addResult(self.currentTest(),FAILURE_STATUS,msg)

    def test(self):
        """User can add functions to be tested in userTests,
            the functions should use self.addSucess() and self.addFailure("") to keep track of the results
            test() will then proceed to autodetect all other tests"""

        self.results=[]
        self._simpleTestList=self.userTests[:]

        for method in dir(self):
            if method.startswith("_test"):
                method=getattr(self,method)
                if isinstance(method,types.FunctionType) or isinstance(method,types.MethodType):
                    self._simpleTestList.append(method)

        try:
            for fonct in self._simpleTestList:
                fonct()
        except testCoreOutOfTests:
            self.addResult("core:critical",CRITICAL_STATUS,"a fatal error occured in test generation line")
        except Exception as e:
            self.addFailure(e)

        return self.results


if __name__ == '__main__':
    term=Terminal()
    mainClasses=testGroup("Main Classes",term,verbose=True,align=40)
    subclass=testGroup("Subgroup",term,"| ",verbose=True,align=40)

    mainTest=testUnit("lambda functions")
    mainTest.addTest(lambda :True)
    mainTest.addTest(lambda :True)
    lambdaTest=testUnit("incorrect lambdas")
    lambdaTest.addTest(lambda x:True)
    lambdaTest.addTest(lambda x,y:True)

    class newTestUnit(testUnit):
        """Just a custom test Class, simple and easyest ?"""
        def __init__(self):
            super(newTestUnit, self).__init__("custom test")

        def test(self):
            self.results=[]

            # Now all the customs test happen, and are append to the results
            potatoe=[]
            try:  # You are supposed to fail this step
                if potatoe[1]==2:
                    self.addResult("empty_table",self.FAILURE_STATUS,"Non empty array")
            except:
                self.addResult("empty_table",SUCESS_STATUS,"")
            potatoe.append([2]*2) # Not try protected, but could be if a bug was a possibility

            try:
                goodinit=True
                for e in potatoe:
                    if e==3:
                        goodinit=False
                        self.addResult("init_table",FAILURE_STATUS,"Wrong elements")
                if goodinit:
                    self.addResult("init_table",SUCESS_STATUS,"")
            except:
                self.addResult("init_table",FAILURE_STATUS,"???")

            return self.results

    class anotherTest(simpleTestUnit):
        """docstring for anotherTest."""
        def __init__(self):
            super(anotherTest, self).__init__("YET ANOTHER TEST")

        def _testCustom(self):
            self.currentTest("testing true")
            if True:
                self.addSucess()
            else:
                self.addFailure("True is False")

            self.currentTest("additions:simple")
            if 1+3==4:
                self.addSucess()
            else:
                self.addFailure("1+3 != 4")

            self.currentTest("error")
            if False:
                self.addSucess()
            else:
                self.addFailure("Supposed to fail")

    mainTest.test()
    lambdaTest.test()

    mainClasses.addTest(lambdaTest)
    subclass.addTest(mainTest)
    mainClasses.addTest(subclass)
    mainClasses.addTest(newTestUnit())
    mainClasses.addTest(anotherTest())
    mainClasses.test()
