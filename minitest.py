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

    def addTest(self,testUnit):
        self._tests.append(testUnit)

    def test(self):
        "Execute all tests, some options might exist at some point"
        sucess,total=0,0
        print self.prefix+"Beggining test group "+self.pretty_group(self.name)
        for test in self._tests:
            print self.prefix+"Testing"+ self.pretty_test(name)
            sucess,total=self.print_result(test.test())
        print self.prefix+"Test finished for test group "+self.pretty_group(self.name)+" "+self.pretty_succesrate(sucess,total)

    def print_result(self,table):
        "Get the array of sucess/failures and print according to the options (still none yet)"
        total=len(table)
        sucess=0
        for item,status,infos in table:
            if status:
                sucess+=1
            print self.prefix+item+"..."+self.pretty_status(status)+self.pretty_info(infos)
        return sucess,total

    def pretty_info(self,infos):
        "Prettyfy the additional infos"
        return self.t.italic(infos)

    def pretty_status(self,status):
        "Prettyfy the status of the test"
        if status:
            return self.t.green("ok")
        return self.t.red("fail")

    def pretty_group(self,name):
        "Prettify the name of the testGroup"
        return self.t.bold(name)

    def pretty_test(self,test):
        "Prettify the name of the testUnit"
        return self.t.underline(test)

    def pretty_succesrate(self,sucess,total):
        if sucess==total:
            wrap=self.t.green
        else:
            wrap=self.t.red
        return wrap("["+str(sucess)+"/"+str(total)+"]")

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
        self.test=[]

    def addTest(self,test):
        "Add a function to the test unit"
        self._tests.append(test)

    def test(self):
        "Execute all tests"
        for test in self._tests:
            try:
                test()
                self.results.append(test,True,'')
            except as e:
                self.results.append(test,False,e)


if __name__ == '__main__':
    term=Terminal()
    mainClasses=testGroup("Main Classes",term)
    #mainClasses.addTest()
    #mainClasses.test()
    testClasses=testUnit("Main classes")
