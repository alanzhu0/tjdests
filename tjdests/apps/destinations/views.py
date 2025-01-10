from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from ..authentication.models import User
from .models import College, Decision, TestScore
from .forms import FilterForm
from django.shortcuts import render

class StudentDestinationListView(
    LoginRequiredMixin, UserPassesTestMixin, ListView
):  # pylint: disable=too-many-ancestors
    model = User
    paginate_by = 20
    
    def get_queryset(self):
        # Superusers can use the "all" GET parameter to see all data
        print(self.request.GET) 
        form = FilterForm(self.request.GET or None)
        
        # Getting Queryset  
        if self.request.GET.get("all", None) is not None:
            if self.request.user.is_superuser and self.request.user.is_staff:
                queryset = User.objects.all()
            else:
                raise PermissionDenied()
        else:
            queryset = User.objects.filter(publish_data=True)

        queryset = queryset.filter(is_senior=True).order_by(
            "last_name", "preferred_name"
        )

        #  Populate the form dynamically
        colleges = College.objects.all()
        decisions = Decision.DECISION_TYPE_CHOICES
        admissions = Decision.ADMIT_TYPE_CHOICES
        form = FilterForm(self.request.GET or None)
        form.fields['college'].choices = [("", "Select a College")] + [(college.id, f"{college.name} - {college.location}") for college in colleges]
        form.fields['decision'].choices = decisions
        form.fields['admission'].choices = admissions

        # Filtering 
        if form.is_valid():
            data = form.cleaned_data
            if data['gpa_min']:
                queryset = queryset.filter(GPA__gte=data['gpa_min'])
            if data['gpa_max']:
                queryset = queryset.filter(GPA__lte=data['gpa_max'])
            if data['college']:
                queryset = queryset.filter(decision__college__id=data['college'])
                if data['decision']:
                    decisions = self.request.GET.getlist('decision')
                    print(decisions)
                    queryset = queryset.filter(decision__decision_type__in=decisions)
                if data['admission']:
                    admissions = self.request.GET.getlist('admission')
                    queryset = queryset.filter(decision__admission_status__in=admissions).distinct()
            # SAT Filters
            sat_min = self.request.GET.get("sat_min", '').strip()
            sat_max = self.request.GET.get("sat_max", '').strip()
            if sat_max != '' and sat_min == '':
                sat_min = "0"
            if sat_min != '' and sat_max == '':
                sat_max = "1600"
            if sat_min != '' or sat_max != '':
                if int(sat_min) > int(sat_max):
                    raise Http404("Invalid SAT score range")
                sat_min = int(sat_min)
                sat_max = int(sat_max)

                sat_filter = Q(testscore__exam_type="SAT_TOTAL")
                if sat_min:
                    sat_filter &= Q(testscore__exam_score__gte=sat_min)
                if sat_max:
                    sat_filter &= Q(testscore__exam_score__lte=sat_max)
                queryset = queryset.filter(sat_filter)

            # ACT Filters
            act_min = self.request.GET.get("act_min", '').strip()
            act_max = self.request.GET.get("act_max", '').strip()
            if act_max != '' and act_min == '':
                act_min = "0"
            if act_min != '' and act_max == '':
                act_max = "36"
            if act_min != '' or act_max != '':
                if int(act_min) > int(act_max):
                    raise Http404("Invalid ACT score range")
                act_min = int(act_min)
                act_max = int(act_max)

                act_filter = Q(testscore__exam_type="ACT_COMP")
                if act_min:
                    act_filter &= Q(testscore__exam_score__gte=act_min)
                if act_max:
                    act_filter &= Q(testscore__exam_score__lte=act_max)
                queryset = queryset.filter(act_filter)

        print(queryset)
        return queryset

    def get_context_data(
        self, *, object_list=None, **kwargs
    ):  # pylint: disable=unused-argument
        context = super().get_context_data(**kwargs)

    
        # Fetch dynamic choices
        colleges = College.objects.all()
        decisions = Decision.DECISION_TYPE_CHOICES
        admissions = Decision.ADMIT_TYPE_CHOICES

        # Populate the form dynamically
        form = FilterForm(self.request.GET or None)
        form.fields['college'].choices = [("", "Select a College")] + [(college.id, f"{college.name} - {college.location}") for college in colleges]
        form.fields['decision'].choices = decisions
        form.fields['admission'].choices = admissions

        context['form'] = form
        college_id = self.request.GET.get("college", None)
        context["college"] = (
            get_object_or_404(College, id=college_id) if college_id else None
        )

        # Sending Context for Filter Message
        context["DECISION"] = ', '.join(self.request.GET.getlist("decision", []))
        context["ADMISSION"] = ', '.join(self.request.GET.getlist("admission", []))
        context["search_query"] = self.request.GET.get("q", None)
        
        context["GPA_MIN"] = self.request.GET.get("gpa_min", "0") or "0"
        context["GPA_MAX"] = self.request.GET.get("gpa_max", "5") or "5"
        context["SAT_MIN"] = self.request.GET.get("sat_min", "0") or "0"
        context["SAT_MAX"] = self.request.GET.get("sat_max", "1600") or "1600"
        context["ACT_MIN"] = self.request.GET.get("act_min", "0") or "0"
        context["ACT_MAX"] = self.request.GET.get("act_max", "36") or "36"
 
        context['COLLEGES'] = College.objects.all()
        context['DECISIONS'] = Decision.DECISION_TYPE_CHOICES
        context['ADMISSIONS'] = Decision.ADMIT_TYPE_CHOICES
        return context
    
    

    def test_func(self):
        assert self.request.user.is_authenticated
        return self.request.user.accepted_terms and not self.request.user.is_banned

    template_name = "destinations/student_list.html"


class CollegeDestinationListView(
    LoginRequiredMixin, UserPassesTestMixin, ListView
):  # pylint: disable=too-many-ancestors
    model = College
    paginate_by = 20

    def get_queryset(self) -> QuerySet:
        search_query = self.request.GET.get("q", None)
        if search_query is not None:
            queryset = College.objects.filter(
                Q(name__icontains=search_query) | Q(location__icontains=search_query)
            )
        else:
            queryset = College.objects.all()

        queryset = (
            queryset.annotate(  # type: ignore  # mypy is annoying
                count_decisions=Count(
                    "decision", filter=Q(decision__user__publish_data=True)
                ),
                count_attending=Count(
                    "decision",
                    filter=Q(
                        decision__in=Decision.objects.filter(
                            attending_college__isnull=False
                        ),
                        decision__user__publish_data=True,
                    ),
                ),
                count_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.ADMIT,
                        decision__user__publish_data=True,
                    ),
                ),
                count_waitlist=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST,
                        decision__user__publish_data=True,
                    ),
                ),
                count_waitlist_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST_ADMIT,
                        decision__user__publish_data=True,
                    ),
                ),
                count_waitlist_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.WAITLIST_DENY,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_ADMIT,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_DENY,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_wl=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_wl_admit=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL_A,
                        decision__user__publish_data=True,
                    ),
                ),
                count_defer_wl_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DEFER_WL_D,
                        decision__user__publish_data=True,
                    ),
                ),
                count_deny=Count(
                    "decision",
                    filter=Q(
                        decision__admission_status=Decision.DENY,
                        decision__user__publish_data=True,
                    ),
                ),
            )
            .filter(count_decisions__gte=1)
            .order_by("name")
        )

        return queryset

    def get_context_data(
        self, *, object_list=None, **kwargs
    ):  # pylint: disable=unused-argument
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("q", None)
        if search_query is not None:
            context["search_query"] = search_query

        return context

    def test_func(self):
        assert self.request.user.is_authenticated
        return self.request.user.accepted_terms and not self.request.user.is_banned

    template_name = "destinations/college_list.html"