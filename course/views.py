from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course, Topic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Create your views here.
class OwnerCourseMixin(LoginRequiredMixin):
    model = Course
    def get_queryset(self):
        qs = super(OwnerCourseMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerCourseEditMixin(OwnerCourseMixin):
    template_name = "course/manage/course/form.html"
    fields = ['topic', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerCourseEditMixin, self).form_valid(form)

class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'course/manage/course/list.html'

class CourseCreateView(OwnerCourseEditMixin, CreateView, PermissionRequiredMixin):
    permission_required = "Can add course"

class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = "Can change course"

class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'course/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = "Can delete course"

from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormset

class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = "course/manage/module/formset.html"
    course = None
    
    def get_formset(self, data=None):
        return ModuleFormset(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course':self.course, 'formset':formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course':self.course, 'formset':formset})

from django.forms.models import modelform_factory
from django.apps import apps
from .models import Content, Module
class ContentCreateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = "course/manage/content/form.html"
    
    def get_model(self, model_name):
        if model_name in ['text', 'file', 'image', 'video']:
            return apps.get_model(app_label='course', model_name=model_name)
        return None

    def get_form(self, model, *arg, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'created', 'updated'])
        return Form(*arg, **kwargs)

    def dispatch(self, request, module_id, model_name):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        return super(ContentCreateView,self).dispatch(request, module_id, model_name)

    def get(self, request, module_id, model_name):
        form = self.get_form(self.model)
        return self.render_to_response({'form': form})

    def post(self, request, module_id, model_name):
        form = self.get_form(self.model, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', module_id)
        return self.render_to_response({'form': formset, 'object':self.obj})

class ContentUpdateView(TemplateResponseMixin, View):
    model = None
    module = None
    obj = None
    template_name = "course/manage/content/form.html"
    def get_model(self, model_name):
        if model_name in ['text', 'file', 'image', 'video']:
            return apps.get_model(app_label='course', model_name=model_name)
        return None

    def get_form(self, model, *arg, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'created', 'updated'])
        return Form(*arg, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super(ContentUpdateView, self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form':form, 'object':self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form':form, 'object':self.obj})

class ContentDeleteView(DeleteView):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = "course/manage/module/content_list.html"
    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        return self.render_to_response({'module': module})

from django.db.models import Count
class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'course/course/list.html'
    
    def get(self, request, topic=None):
        topics = Topic.objects.annotate(total_courses=Count('courses'))
        courses = Course.objects.annotate(total_modules=Count('modules'))
     
        if topic:
            topic = get_object_or_404(Topic, slug=topic)
            courses = courses.filter(topic__in=[topic])

        return self.render_to_response({'topics': topics, 'topic': topic, 'courses': courses})

from student.forms import CourseEnrollForm
from django.views.generic.detail import DetailView
class CourseDetailView(DetailView):
    model = Course
    template_name = "course/course/detail.html"

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        return context

