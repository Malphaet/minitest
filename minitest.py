#!/usr/bin/env python

# Copyleft (c) 2016 Cocobug All Rights Reserved.

from blessings import Terminal
__all__ =["testGroup","testUnit"]

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
        self.verbose=verbose
        self.align=align

    def addTest(self,testUnit):
        self._tests.append(testUnit)

    def test(self):
        "Execute all tests, some options might exist at some point"
        module_sucess,module_total=0,0

        #print self.prefix+"+"+"-"*(max(0,self.align+7-len(self.prefix)))
        print self.prefix+"+ Executing test group "+self.pretty_group(self.name)
        oldprefix=self.prefix
        self.prefix+="|  "
        self.results=[]

        for test in self._tests:
            try:
                sucess,total,failures=self.print_result(test.test())
            except:
                sucess,total,failures=self.print_result([])

            print self.pretty_subtests(test.name,sucess,total)

            if sucess==total:
                module_sucess+=1
            module_total+=1
            for failure in failures:
                print failure
            self.results.append([self,True,""])
        self.prefix=oldprefix

        print self.pretty_group_result(module_sucess,module_total)
        #print self.prefix+"+"+"-"*(max(0,self.align+7-len(self.prefix)))
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
        if (self.align>lenbloc+4):
            dots="."*(self.align-lenbloc)
        else:
            dots="...."
        return dots

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
                self.addResult(test,True,'')
            except Exception as e:
                self.addResult(test,False,e)
        return self.results

    def addResult(self,testName,status,info):
        self.results.append([testName,status,info])


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
        """Just a custom test Class"""
        def __init__(self):
            super(newTestUnit, self).__init__("custom test")

        def test(self):
            self.results=[]

            # Now all the customs test happen, and are append to the results

            potatoe=[]

            try:  # You are supposed to fail this step
                if potatoe[1]==2:
                    self.addResult("empty_table",False,"Non empty array")
            except:
                self.addResult("empty_table",True,"")

            potatoe.append([2]*2) # Not try protected, but could be if a bug was a possibility

            try:
                goodinit=True
                for e in potatoe:
                    if e==3:
                        goodinit=False
                        self.addResult("init_table",False,"Wrong elements")
                if goodinit:
                    self.addResult("init_table",True,"")
            except:
                self.addResult("init_table",False,"???")

            return self.results


    mainTest.test()
    lambdaTest.test()

    mainClasses.addTest(lambdaTest)
    subclass.addTest(mainTest)
    mainClasses.addTest(subclass)
    mainClasses.addTest(newTestUnit())

    mainClasses.test()
