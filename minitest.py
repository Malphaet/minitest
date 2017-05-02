#!/usr/bin/env python

# Copyleft (c) 2016 Cocobug All Rights Reserved.

from blessings import Terminal

class testGroup(object):
    """TestGroup, group a number of testUnit, exec them and print the results"""
    def __init__(self,name="",terminal=None,prefix=""):
        self._tests=[]
        self.name=name
        self.t=terminal
        self.prefix=prefix
        if self.t==None:
            self.t=Terminal()
        self.results=[]
        self.sucess_text= self.t.green("sucess")
        self.failure_text=self.t.bright_red("failure")

    def addTest(self,testUnit):
        self._tests.append(testUnit)

    def test(self):
        "Execute all tests, some options might exist at some point"
        module_sucess,module_total=0,0
        oldprefix=self.prefix
        print self.prefix+"+ Executing test group "+self.pretty_group(self.name)
        self.prefix+="| "
        self.results=[]

        for test in self._tests:
            sucess,total,failures=self.print_result(test.test())
            print self.prefix+"testing "+ self.pretty_test(test.name)+" .... "+self.pretty_succesrate(sucess,total)
            if sucess==total:
                module_sucess+=1
            module_total+=1
            for failure in failures:
                print self.prefix+" * "+failure
            self.results.append([self,True,""])
        self.prefix=oldprefix

        print self.prefix+"+ Done "+self.pretty_group(self.name)+" "+self.pretty_succesrate(module_sucess,module_total)
        return self.results

    def print_result(self,table):
        "Get the array of sucess/failures and print according to the options (still none yet)"
        total=len(table)
        sucess=0
        array_of_failures=[]
        nb=0

        for item,status,infos in table:
            nb+=1
            if status:
                sucess+=1
            else:
                array_of_failures.append(self.pretty_status(status)+" "+"line "+str(nb)+" : "+item.__name__.strip("<>")+" .... "+self.pretty_info(infos))
        return sucess,total,array_of_failures

    def pretty_info(self,infos):
        "Prettyfy the additional infos"
        if infos=="":
            return ""
        return self.t.italic(" ("+str(infos)+")")

    def pretty_status(self,status):
        "Prettyfy the status of the test"
        if status:
            return self.sucess_text
        return self.failure_text

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
                self.results.append([test,True,''])
            except Exception as e:
                self.results.append([test,False,e])
        return self.results

if __name__ == '__main__':
    term=Terminal()
    mainClasses=testGroup("Main Classes",term)
    subclass=testGroup("Subgroup",term,"| ")

    mainTest=testUnit("basic_inputs")
    mainTest.addTest(lambda :True)
    mainTest.addTest(lambda :True)
    lambdaTest=testUnit("lambda")
    lambdaTest.addTest(lambda x:True)
    lambdaTest.addTest(lambda :True)

    mainTest.test()
    lambdaTest.test()

    mainClasses.addTest(lambdaTest)
    subclass.addTest(mainTest)
    mainClasses.addTest(subclass)

    mainClasses.test()
